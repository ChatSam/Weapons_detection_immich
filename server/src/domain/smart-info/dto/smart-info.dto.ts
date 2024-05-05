import { ApiProperty } from '@nestjs/swagger';
import { ValidateUUID } from '../../domain.util';
import { Type } from 'class-transformer';
import { IsArray, ValidateNested } from 'class-validator';
import { MediaMode } from '@app/domain/repositories';

export class WeaponsDetectResponseDto {
    @ValidateUUID()
    id!: string;
    // @IsArray()
    // @ValidateNested({ each: true })
    // @Type(() => WeaponsDetectItem)
    // data!: WeaponsDetectItem[];
    @ApiProperty({ type: 'string', description: 'Path to the media file' })
    filePath!: string;
    @ApiProperty({ type: 'string', description: 'Media type (image|video)' })
    mediaMode!: MediaMode;
  }

// export class WeaponsDetectItem {
//     @ApiProperty({ type: 'string', description: 'base-64 encoded image' })
//     image!: string;
//     @ApiProperty({ type: 'number' })
//     score!: number;
// }