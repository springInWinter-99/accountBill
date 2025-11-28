import api from './axios'

export const billsApi = {
  getBills: (params = {}) => {
    return api.get('/bills', { params })
  },
  
  getBill: (id) => {
    return api.get(`/bills/${id}`)
  },
  
  createBill: (billData) => {
    return api.post('/bills', billData)
  },
  
  updateBill: (id, billData) => {
    return api.put(`/bills/${id}`, billData)
  },
  
  deleteBill: (id) => {
    return api.delete(`/bills/${id}`)
  },
  
  getStatistics: (params = {}) => {
    return api.get('/bills/statistics/summary', { params })
  }
}
