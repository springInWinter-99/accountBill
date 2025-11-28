import api from './axios'

export const imagesApi = {
  // 上传单张图片
  uploadImage: (file, autoCreateBill = true) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('auto_create_bill', autoCreateBill)
    return api.post('/images/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 60000 // 60秒超时，因为OCR需要时间
    })
  },
  
  // 批量上传图片
  uploadImages: (files, autoCreateBill = true) => {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })
    formData.append('auto_create_bill', autoCreateBill)
    return api.post('/images/upload/batch', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 300000 // 5分钟超时
    })
  },
  
  // 获取图片信息
  getImage: (id) => {
    return api.get(`/images/${id}`)
  },
  
  // 获取图片文件
  getImageFile: (id) => {
    return api.get(`/images/${id}/file`, {
      responseType: 'blob'
    })
  },
  
  // 获取账单的所有图片
  getBillImages: (billId) => {
    return api.get(`/images/bill/${billId}/images`)
  },
  
  // 删除图片
  deleteImage: (id) => {
    return api.delete(`/images/${id}`)
  },
  
  // 重新解析图片
  reparseImage: (id, autoCreateBill = false) => {
    return api.post(`/images/${id}/reparse`, null, {
      params: { auto_create_bill: autoCreateBill },
      timeout: 60000
    })
  }
}
