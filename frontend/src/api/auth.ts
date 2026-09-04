import { apiRequest } from './client';
import { User, AuthTokenResponse, UserRole } from '../types/auth';

export async function registerApi(email: string, password: string, role: UserRole = 'candidate', classLevel?: number): Promise<User> {
  return apiRequest<User>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, role, class_level: role === 'candidate' ? classLevel : undefined }),
  });
}

export async function loginApi(email: string, password: string): Promise<AuthTokenResponse> {
  return apiRequest<AuthTokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function getMeApi(): Promise<User> {
  return apiRequest<User>('/auth/me');
}
