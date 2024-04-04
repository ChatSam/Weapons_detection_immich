import { ApiProperty } from '@nestjs/swagger';
import { ValidateUUID } from '../../domain.util';
import { Type } from 'class-transformer';
import { IsArray, ValidateNested } from 'class-validator';

export class WeaponsDetectResponseDto {
    @ValidateUUID()
    id!: string;
    @IsArray()
    @ValidateNested({ each: true })
    @Type(() => AssetFaceUpdateItem)
    data!: WeaponsDetectItem[];
  }

export class WeaponsDetectItem {
    @ApiProperty({ type: 'base-64 encoded image' })
    image!: string;
    @ApiProperty({ type: 'number' })
    score!: number;
}