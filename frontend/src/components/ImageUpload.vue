<template>
  <div class="image-upload">
    <el-upload
      ref="uploadRef"
      :action="uploadUrl"
      :headers="uploadHeaders"
      :data="uploadData"
      :file-list="fileList"
      :auto-upload="false"
      :on-change="handleFileChange"
      :on-remove="handleFileRemove"
      :before-upload="beforeUpload"
      :on-success="handleUploadSuccess"
      :on-error="handleUploadError"
      :limit="maxFiles"
      multiple
      accept="image/*"
      drag
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        将图片拖到此处，或<em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持上传支付宝、微信账单图片，自动识别并创建账单（最多{{ maxFiles }}张）
        </div>
      </template>
    </el-upload>

    <div v-if="fileList.length > 0" class="upload-actions">
      <el-button type="primary" @click="handleUpload" :loading="uploading" :disabled="uploading">
        {{ uploading ? '上传中...' : `上传 ${fileList.length} 张图片` }}
      </el-button>
      <el-button @click="handleClear">清空</el-button>
      <el-checkbox v-model="autoCreateBill" style="margin-left: 20px">
        自动创建账单
      </el-checkbox>
    </div>

    <!-- 上传结果 -->
    <div v-if="uploadResults.length > 0" class="upload-results">
      <el-divider>上传结果</el-divider>
      <el-card v-for="(result, index) in uploadResults" :key="index" class="result-card" shadow="hover">
        <div class="result-header">
          <span class="result-filename">{{ result.filename }}</span>
          <el-tag :type="result.success ? 'success' : 'danger'">
            {{ result.success ? '成功' : '失败' }}
          </el-tag>
        </div>
        <div v-if="result.success && result.bill" class="result-content">
          <p><strong>账单标题：</strong>{{ result.bill.title }}</p>
          <p><strong>金额：</strong>
            <span :class="result.bill.category === '收入' ? 'income' : 'expense'">
              {{ result.bill.category === '收入' ? '+' : '-' }}¥{{ result.bill.amount }}
            </span>
          </p>
          <p><strong>分类：</strong>{{ result.bill.category }}</p>
          <p><strong>类型：</strong>{{ result.bill.type }}</p>
          <p><strong>日期：</strong>{{ result.bill.bill_date }}</p>
        </div>
        <div v-else-if="!result.success" class="result-error">
          <p><strong>错误：</strong>{{ result.error }}</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { imagesApi } from '../api/images'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  maxFiles: {
    type: Number,
    default: 20
  }
})

const emit = defineEmits(['upload-success'])

const uploadRef = ref(null)
const fileList = ref([])
const uploading = ref(false)
const autoCreateBill = ref(true)
const uploadResults = ref([])

const authStore = useAuthStore()

const uploadUrl = computed(() => {
  // 不使用action，手动上传
  return ''
})

const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${authStore.token}`
}))

const uploadData = computed(() => ({
  auto_create_bill: autoCreateBill.value
}))

const handleFileChange = (file, files) => {
  fileList.value = files
}

const handleFileRemove = (file, files) => {
  fileList.value = files
}

const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isImage) {
    ElMessage.error('只能上传图片文件！')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过 10MB！')
    return false
  }
  return false // 阻止自动上传
}

const handleUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择图片')
    return
  }

  uploading.value = true
  uploadResults.value = []

  try {
    const files = fileList.value.map(item => item.raw)
    
    if (files.length === 1) {
      // 单张上传
      const response = await imagesApi.uploadImage(files[0], autoCreateBill.value)
      uploadResults.value = [{
        filename: response.data.image.filename,
        success: response.data.image.parse_status === 'success',
        bill: response.data.bill,
        error: response.data.image.parse_error
      }]
      
      if (response.data.bill) {
        ElMessage.success('上传成功，账单已创建')
        emit('upload-success', response.data.bill)
      } else {
        ElMessage.warning('图片上传成功，但未能识别账单信息')
      }
    } else {
      // 批量上传
      const response = await imagesApi.uploadImages(files, autoCreateBill.value)
      uploadResults.value = response.data.results.map((result, index) => ({
        filename: fileList.value[index]?.name || '未知文件',
        success: result.image && result.image.parse_status === 'success',
        bill: result.bill || null,
        error: result.image?.parse_error || '上传失败'
      }))
      
      const successCount = response.data.success_count
      const failedCount = response.data.failed_count
      
      if (successCount > 0) {
        ElMessage.success(`成功上传 ${successCount} 张图片${failedCount > 0 ? `，失败 ${failedCount} 张` : ''}`)
        emit('upload-success')
      } else {
        ElMessage.error('所有图片上传失败')
      }
    }
  } catch (error) {
    ElMessage.error('上传失败：' + (error.response?.data?.detail || error.message))
  } finally {
    uploading.value = false
  }
}

const handleUploadSuccess = (response, file) => {
  // 手动上传，不使用此回调
}

const handleUploadError = (error, file) => {
  ElMessage.error(`上传失败：${file.name}`)
}

const handleClear = () => {
  fileList.value = []
  uploadResults.value = []
  uploadRef.value?.clearFiles()
}
</script>

<style scoped>
.image-upload {
  width: 100%;
}

.upload-actions {
  margin-top: 20px;
  display: flex;
  align-items: center;
}

.upload-results {
  margin-top: 20px;
}

.result-card {
  margin-bottom: 10px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.result-filename {
  font-weight: bold;
  color: #333;
}

.result-content {
  margin-top: 10px;
}

.result-content p {
  margin: 5px 0;
  color: #666;
}

.result-error {
  margin-top: 10px;
  color: #f56c6c;
}

.income {
  color: #67c23a;
  font-weight: bold;
}

.expense {
  color: #f56c6c;
  font-weight: bold;
}
</style>
