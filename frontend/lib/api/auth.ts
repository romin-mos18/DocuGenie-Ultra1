import api from './axios';
import { User } from '../../app/store/slices/authSlice';

interface LoginData {
  email: string;
  password: string;
}

interface RegisterData {
  name: string;
  email: string;
  password: string;
}

interface AuthResponse {
  token: string;
  refreshToken: string;
  user: User;
}

export const authApi = {
  login: async (data: LoginData): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', data);
    return response.data;
  },

  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/register', data);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  },

  refreshToken: async (refreshToken: string): Promise<{ token: string }> => {
    const response = await api.post<{ token: string }>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  getProfile: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await api.put<User>('/users/profile', data);
    return response.data;
  },

  updatePassword: async (data: {
    currentPassword: string;
    newPassword: string;
  }): Promise<void> => {
    await api.put('/users/password', data);
  },

  updateAvatar: async (file: File): Promise<User> => {
    const formData = new FormData();
    formData.append('avatar', file);
    const response = await api.put<User>('/users/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};
