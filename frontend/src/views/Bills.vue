<template>
  <div class="bills-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="statistics-row">
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-label">总收入</div>
            <div class="stat-value income">¥{{ statistics.total_income || '0.00' }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-label">总支出</div>
            <div class="stat-value expense">¥{{ statistics.total_expense || '0.00' }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-label">余额</div>
            <div class="stat-value" :class="balanceClass">
              ¥{{ statistics.balance || '0.00' }}
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-label">账单数量</div>
            <div class="stat-value">{{ statistics.count || 0 }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 操作栏 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="分类">
          <el-select v-model="filterForm.category" placeholder="全部" clearable style="width: 150px">
            <el-option label="收入" value="收入" />
            <el-option label="支出" value="支出" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="filterForm.start_date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="filterForm.end_date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadBills">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
          <el-button type="success" @click="handleAdd">新增账单</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 账单列表 -->
    <el-card>
      <el-table :data="bills" style="width: 100%" v-loading="loading">
        <el-table-column prop="title" label="标题" width="200" />
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="scope">
            <span :class="scope.row.category === '收入' ? 'income' : 'expense'">
              {{ scope.row.category === '收入' ? '+' : '-' }}¥{{ scope.row.amount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.category === '收入' ? 'success' : 'danger'">
              {{ scope.row.category }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="bill_date" label="日期" width="120" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      @close="resetForm"
    >
      <el-form :model="billForm" :rules="billRules" ref="billFormRef" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="billForm.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="金额" prop="amount">
          <el-input-number
            v-model="billForm.amount"
            :precision="2"
            :min="0"
            style="width: 100%"
            placeholder="请输入金额"
          />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-radio-group v-model="billForm.category">
            <el-radio label="收入">收入</el-radio>
            <el-radio label="支出">支出</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="billForm.type" placeholder="请选择类型" style="width: 100%">
            <el-option label="餐饮" value="餐饮" />
            <el-option label="交通" value="交通" />
            <el-option label="购物" value="购物" />
            <el-option label="娱乐" value="娱乐" />
            <el-option label="工资" value="工资" />
            <el-option label="奖金" value="奖金" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期" prop="bill_date">
          <el-date-picker
            v-model="billForm.bill_date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="billForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { billsApi } from '../api/bills'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const submitting = ref(false)
const bills = ref([])
const statistics = ref({
  total_income: '0.00',
  total_expense: '0.00',
  balance: '0.00',
  count: 0
})

const filterForm = reactive({
  category: '',
  start_date: '',
  end_date: ''
})

const dialogVisible = ref(false)
const dialogTitle = ref('新增账单')
const billFormRef = ref(null)
const currentBillId = ref(null)

const billForm = reactive({
  title: '',
  amount: 0,
  category: '支出',
  type: '',
  bill_date: '',
  description: ''
})

const billRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  amount: [{ required: true, message: '请输入金额', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  type: [{ required: true, message: '请选择类型', trigger: 'blur' }],
  bill_date: [{ required: true, message: '请选择日期', trigger: 'change' }]
}

const balanceClass = computed(() => {
  const balance = parseFloat(statistics.value.balance || 0)
  return balance >= 0 ? 'income' : 'expense'
})

const loadBills = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterForm.category) params.category = filterForm.category
    if (filterForm.start_date) params.start_date = filterForm.start_date
    if (filterForm.end_date) params.end_date = filterForm.end_date

    const [billsResponse, statsResponse] = await Promise.all([
      billsApi.getBills(params),
      billsApi.getStatistics(params)
    ])
    
    bills.value = billsResponse.data
    statistics.value = statsResponse.data
  } catch (error) {
    ElMessage.error('加载账单失败')
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.category = ''
  filterForm.start_date = ''
  filterForm.end_date = ''
  loadBills()
}

const handleAdd = () => {
  dialogTitle.value = '新增账单'
  currentBillId.value = null
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑账单'
  currentBillId.value = row.id
  billForm.title = row.title
  billForm.amount = parseFloat(row.amount)
  billForm.category = row.category
  billForm.type = row.type
  billForm.bill_date = row.bill_date
  billForm.description = row.description || ''
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这条账单吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await billsApi.deleteBill(row.id)
    ElMessage.success('删除成功')
    loadBills()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!billFormRef.value) return
  
  await billFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (currentBillId.value) {
          await billsApi.updateBill(currentBillId.value, billForm)
          ElMessage.success('更新成功')
        } else {
          await billsApi.createBill(billForm)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadBills()
      } catch (error) {
        ElMessage.error(currentBillId.value ? '更新失败' : '创建失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const resetForm = () => {
  billForm.title = ''
  billForm.amount = 0
  billForm.category = '支出'
  billForm.type = ''
  billForm.bill_date = ''
  billForm.description = ''
  if (billFormRef.value) {
    billFormRef.value.clearValidate()
  }
}

onMounted(() => {
  loadBills()
})
</script>

<style scoped>
.bills-container {
  max-width: 1200px;
  margin: 0 auto;
}

.statistics-row {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
}

.stat-value.income {
  color: #67c23a;
}

.stat-value.expense {
  color: #f56c6c;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  margin: 0;
}

.income {
  color: #67c23a;
}

.expense {
  color: #f56c6c;
}
</style>
