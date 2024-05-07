import path from 'node:path';
import { CLIPConfig, RecognitionConfig, WeaponsDetectConfig } from '../smart-info/dto';

export const IMachineLearningRepository = 'IMachineLearningRepository';

export interface VisionModelInput {
  imagePath: string;
}

export interface TextModelInput {
  text: string;
}
export interface VideoModelInput {
  videoPath: string;
}
export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface DetectFaceResult {
  imageWidth: number;
  imageHeight: number;
  boundingBox: BoundingBox;
  score: number;
  embedding: number[];
}

export interface DetectWeaponsResult {
  filePath: string; //Path to the image
}

export enum ModelType {
  FACIAL_RECOGNITION = 'facial-recognition',
  CLIP = 'clip',
  WEAPONS_DETECTION = 'weapons-detection',
}

export enum CLIPMode {
  VISION = 'vision',
  TEXT = 'text',
}

//added MediaMode to determine if the input is a video or image
export enum MediaMode {
  VIDEO = 'video',
  IMAGE = 'image',
}

export interface IMachineLearningRepository {
  encodeImage(url: string, input: VisionModelInput, config: CLIPConfig): Promise<number[]>;
  encodeText(url: string, input: TextModelInput, config: CLIPConfig): Promise<number[]>;
  detectFaces(url: string, input: VisionModelInput, config: RecognitionConfig): Promise<DetectFaceResult[]>;
  detectWeaponsInImage(url: string, input: VisionModelInput, config: WeaponsDetectConfig): Promise<DetectWeaponsResult>;
  detectWeaponsInVideo(url: string, input: VideoModelInput, config: WeaponsDetectConfig): Promise<DetectWeaponsResult>;
}
