export const API_BASE_URL = "/api";

export async function requestJson<TResponse>(
  path: string,
  init?: RequestInit,
): Promise<TResponse> {
  throw new Error(
    `API client placeholder is not connected yet: ${API_BASE_URL}${path}`,
  );
}
