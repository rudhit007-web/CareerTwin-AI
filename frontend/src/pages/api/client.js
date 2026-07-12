import axios from 'axios'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL })

// Attach the JWT token from localStorage on every request.
// axios.create() instances do NOT inherit axios.defaults, so we
// must read the token explicitly via an interceptor.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('ct_token')
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

// If the server returns 401 (expired/invalid token), clear storage
// and redirect to the login page so the user re-authenticates.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('ct_token')
      window.location.href = '/auth'
    }
    return Promise.reject(error)
  }
)

export const profileAPI = {
  get:    ()       => api.get('/profile'),
  update: (data)   => api.put('/profile', data),
}

export const resumeAPI = {
  upload:  (file)  => {
    const fd = new FormData()
    fd.append('file', file)
    return api.post('/resume/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  analyze: ()      => api.post('/resume/analyze'),
  get:     ()      => api.get('/resume'),
}

export const careerAPI = {
  runSkillGap:  (data)   => api.post('/career/skill-gap', data),
  getSkillGap:  ()       => api.get('/career/skill-gap'),
  runRoadmap:   ()       => api.post('/career/roadmap'),
  getRoadmap:   ()       => api.get('/career/roadmap'),
  runProjects:  (data)   => api.post('/career/projects', data),
  getProjects:  ()       => api.get('/career/projects'),
}

export const chatAPI = {
  getSessions:   ()           => api.get('/chat/sessions'),
  createSession: (data)       => api.post('/chat/sessions', data),
  getSession:    (id)         => api.get(`/chat/sessions/${id}`),
  deleteSession: (id)         => api.delete(`/chat/sessions/${id}`),
  sendMessage:   (id, msg)    => api.post(`/chat/sessions/${id}/send`, { message: msg }),
}

export const dashboardAPI = {
  get: () => api.get('/dashboard'),
}

export const documentsAPI = {
  list:   ()    => api.get('/documents'),
  delete: (id)  => api.delete(`/documents/${id}`),
}

export default api
