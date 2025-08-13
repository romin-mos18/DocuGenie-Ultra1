import api from './axios';
import { User } from '../../app/store/slices/authSlice';

interface UserListResponse {
  users: User[];
  total: number;
}

interface UserFilters {
  role?: string;
  searchTerm?: string;
}

export const usersApi = {
  getUsers: async (
    page: number = 1,
    limit: number = 10,
    filters?: UserFilters
  ): Promise<UserListResponse> => {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(filters?.role && { role: filters.role }),
      ...(filters?.searchTerm && { search: filters.searchTerm }),
    });

    const response = await api.get<UserListResponse>(`/users?${params}`);
    return response.data;
  },

  getUser: async (id: number): Promise<User> => {
    const response = await api.get<User>(`/users/${id}`);
    return response.data;
  },

  createUser: async (data: {
    name: string;
    email: string;
    password: string;
    role: string;
  }): Promise<User> => {
    const response = await api.post<User>('/users', data);
    return response.data;
  },

  updateUser: async (id: number, data: Partial<User>): Promise<User> => {
    const response = await api.put<User>(`/users/${id}`, data);
    return response.data;
  },

  deleteUser: async (id: number): Promise<void> => {
    await api.delete(`/users/${id}`);
  },

  getUserActivity: async (id: number): Promise<{
    documents: number;
    uploads: number;
    lastActive: string;
  }> => {
    const response = await api.get(`/users/${id}/activity`);
    return response.data;
  },

  updateUserRole: async (id: number, role: string): Promise<User> => {
    const response = await api.put<User>(`/users/${id}/role`, { role });
    return response.data;
  },

  disableUser: async (id: number): Promise<void> => {
    await api.put(`/users/${id}/disable`);
  },

  enableUser: async (id: number): Promise<void> => {
    await api.put(`/users/${id}/enable`);
  },

  resetPassword: async (id: number): Promise<{ temporaryPassword: string }> => {
    const response = await api.post<{ temporaryPassword: string }>(`/users/${id}/reset-password`);
    return response.data;
  },
};
