import { AuthDto, WeaponsDetectResponseDto, SmartInfoService } from '@app/domain';
import {Controller, Get, Param} from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import { Auth, Authenticated } from '../app.guard';
import { UseValidation } from '../app.utils';
import { UUIDParamDto } from './dto/uuid-param.dto';

@ApiTags('WeaponsDetect')
@Controller('weapons-detect')
@Authenticated()
@UseValidation()
export class WeaponsDetectController {
  constructor(private service: SmartInfoService) {}

  @Get(':id')
  getWeaponsDetect(@Auth() auth: AuthDto, @Param() { id }: UUIDParamDto): Promise<WeaponsDetectResponseDto> {
    return this.service.handleDetectWeapons(auth, id);
  }
  
}

