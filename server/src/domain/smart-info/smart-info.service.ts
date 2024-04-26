import { ImmichLogger } from '@app/infra/logger';
import { Inject, Injectable, BadRequestException } from '@nestjs/common';
import { usePagination } from '../domain.util';
import { IBaseJob, IEntityJob, JOBS_ASSET_PAGINATION_SIZE, JobName, QueueName } from '../job';
import {
  IAccessRepository,
  DatabaseLock,
  IAssetRepository,
  IDatabaseRepository,
  IJobRepository,
  IMachineLearningRepository,
  ISmartInfoRepository,
  ISystemConfigRepository,
  WithoutProperty,
} from '../repositories';
import { SystemConfigCore } from '../system-config';
import { AccessCore, Permission } from '../access';
import { AuthDto } from '../auth';
import { WeaponsDetectResponseDto } from './dto/smart-info.dto';

@Injectable()
export class SmartInfoService {
  private configCore: SystemConfigCore;
  private logger = new ImmichLogger(SmartInfoService.name);
  private access: AccessCore;

  constructor(
    @Inject(IAccessRepository) accessRepository: IAccessRepository,
    @Inject(IAssetRepository) private assetRepository: IAssetRepository,
    @Inject(IDatabaseRepository) private databaseRepository: IDatabaseRepository,
    @Inject(IJobRepository) private jobRepository: IJobRepository,
    @Inject(IMachineLearningRepository) private machineLearning: IMachineLearningRepository,
    @Inject(ISmartInfoRepository) private repository: ISmartInfoRepository,
    @Inject(ISystemConfigRepository) configRepository: ISystemConfigRepository,
  ) {
    this.access = AccessCore.create(accessRepository);
    this.configCore = SystemConfigCore.create(configRepository);
  }

  async init() {
    await this.jobRepository.pause(QueueName.SMART_SEARCH);

    await this.jobRepository.waitForQueueCompletion(QueueName.SMART_SEARCH);

    const { machineLearning } = await this.configCore.getConfig();

    await this.databaseRepository.withLock(DatabaseLock.CLIPDimSize, () =>
      this.repository.init(machineLearning.clip.modelName),
    );

    await this.jobRepository.resume(QueueName.SMART_SEARCH);
  }

  async handleQueueEncodeClip({ force }: IBaseJob) {
    const { machineLearning } = await this.configCore.getConfig();
    if (!machineLearning.enabled || !machineLearning.clip.enabled) {
      return true;
    }

    const assetPagination = usePagination(JOBS_ASSET_PAGINATION_SIZE, (pagination) => {
      return force
        ? this.assetRepository.getAll(pagination)
        : this.assetRepository.getWithout(pagination, WithoutProperty.SMART_SEARCH);
    });

    for await (const assets of assetPagination) {
      await this.jobRepository.queueAll(
        assets.map((asset) => ({ name: JobName.SMART_SEARCH, data: { id: asset.id } })),
      );
    }

    return true;
  }

  async handleEncodeClip({ id }: IEntityJob) {
    const { machineLearning } = await this.configCore.getConfig();
    if (!machineLearning.enabled || !machineLearning.clip.enabled) {
      return true;
    }

    const [asset] = await this.assetRepository.getByIds([id]);
    if (!asset.resizePath) {
      return false;
    }

    const clipEmbedding = await this.machineLearning.encodeImage(
      machineLearning.url,
      { imagePath: asset.resizePath },
      machineLearning.clip,
    );

    if (this.databaseRepository.isBusy(DatabaseLock.CLIPDimSize)) {
      this.logger.verbose(`Waiting for CLIP dimension size to be updated`);
      await this.databaseRepository.wait(DatabaseLock.CLIPDimSize);
    }

    await this.repository.upsert({ assetId: asset.id }, clipEmbedding);

    return true;
  }

  async handleDetectWeapons(auth: AuthDto, id: string): Promise<WeaponsDetectResponseDto> {
    await this.access.requirePermission(auth, Permission.ASSET_READ, id);

    const { machineLearning } = await this.configCore.getConfig();
    if (!machineLearning.enabled || !machineLearning.weaponsDetection.enabled){
      throw new BadRequestException('Machine learning is disabled');
    }

    const asset = await this.assetRepository.getById(id);

    if (!asset) {
      throw new BadRequestException('Asset not found');
    }

    if (!asset.resizePath) {
      throw new BadRequestException('Asset has no image file path');
    }

    const detectedWeapons = await this.machineLearning.detectWeapons(
      machineLearning.url,
      { imagePath: asset.resizePath },
      machineLearning.weaponsDetection,
    );

    const response = {
      id: id,
      data: detectedWeapons.map((weapon) => ({
        image: weapon.image,
        score: weapon.score,
      })),
    };

    return response;
  }

}
