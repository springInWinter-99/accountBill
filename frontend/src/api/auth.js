import api from './axios'

export const authApi = {
  login: (username, password) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    return api.post('/auth/login', formData)
  },
  
  register: (userData) => {
    return api.post('/auth/register', userData)
  },
  
  getCurrentUser: () => {
    return api.get('/auth/me')
  }
}
