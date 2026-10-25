const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiRequestError extends Error {
  constructor(message: string, public code = "request_failed") {
    super(message);
  }
}

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiRequestError(body?.error?.message ?? "Something went wrong", body?.error?.code);
  }
  return body as T;
}

