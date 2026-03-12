/** Tipos globales de la capa API */

export type ApiErrorDetail = string | Record<string, unknown> | Array<unknown>;

export interface ApiError {
  detail: ApiErrorDetail;
  status: number;
}
