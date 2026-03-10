<template>
  <div class="group-list-page">
    <el-container style="height: calc(100vh - 140px); border: 1px solid #eee;">
      <!-- 左侧分组树 -->
      <el-aside width="250px" style="background-color: #fff; border-right: 1px solid #eee; padding: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
          <span>分组</span>
          <el-button type="primary" size="mini" icon="el-icon-plus" @click="handleAddGroup">新增</el-button>
        </div>
        <el-input placeholder="请输入分组名称" v-model="groupSearch" prefix-icon="el-icon-search" size="small" style="margin-bottom: 10px;"></el-input>
        <el-tree :data="groupTree" :props="defaultProps" default-expand-all :expand-on-click-node="false" @node-click="handleNodeClick">
          <span class="custom-tree-node" slot-scope="{ node, data }">
            <span>{{ node.label }}</span>
            <span class="tree-actions">
              <i class="el-icon-edit" @click.stop="handleEditGroup(data)"></i>
              <i class="el-icon-delete" @click.stop="handleDeleteGroup(node, data)"></i>
            </span>
          </span>
        </el-tree>
      </el-aside>

      <!-- 右侧分组详情 -->
      <el-main style="padding: 20px;">
        <div class="page-header" style="margin-bottom: 20px; border-bottom: 1px solid #ebeef5; padding-bottom: 10px;">
          <span style="font-size: 16px; font-weight: bold;">分组设备 / 详情</span>
        </div>

        <div class="filter-container" style="display: flex; justify-content: space-between; margin-bottom: 20px;">
          <div style="display: flex;">
            <el-input v-model="deviceSearch" placeholder="设备名称、SN编号、地址" style="width: 300px; margin-right: 10px;" size="small"></el-input>
            <el-button type="primary" icon="el-icon-search" size="small" @click="handleSearch">搜索</el-button>
          </div>
          <el-button type="primary" icon="el-icon-plus" size="small">添加到分组</el-button>
        </div>

        <el-table :data="groupDevices" v-loading="loading" style="width: 100%" :header-cell-style="{background:'#f5f7fa',color:'#606266'}" @selection-change="handleSelectionChange">
          <el-table-column type="selection" width="55"></el-table-column>
          <el-table-column prop="name" label="设备名称"></el-table-column>
          <el-table-column prop="creator" label="创建人" width="100"></el-table-column>
          <el-table-column prop="sn" label="网关SN编号" width="150"></el-table-column>
          <el-table-column prop="status" label="网关状态" width="100">
            <template slot-scope="scope">
              <span :class="scope.row.status === '在线' ? 'status-online' : 'status-offline'">{{ scope.row.status }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="address" label="所在地"></el-table-column>
          <el-table-column label="操作" width="100">
            <template slot-scope="scope">
              <el-button type="text" size="small" class="text-danger" @click="handleRemoveDevice(scope.row)">移出分组</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container" style="margin-top: 20px; display: flex; justify-content: space-between; align-items: center;">
          <div>
            <el-button size="small" @click="handleBatchRemove" :disabled="selectedDevices.length === 0">移出分组</el-button>
          </div>
          <div style="display: flex; align-items: center;">
            <span style="margin-right: 10px; color: #606266;">共有{{ total }}条</span>
            <el-pagination
              background
              layout="prev, pager, next, sizes"
              :total="total"
              :page-size="pageSize"
              :page-sizes="[10, 20, 50]"
              :current-page.sync="currentPage"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange">
            </el-pagination>
          </div>
        </div>
      </el-main>
    </el-container>

    <!-- 分组编辑/新增弹窗 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="500px">
      <el-form :model="groupForm" label-width="100px" :rules="groupRules" ref="groupForm">
        <el-form-item label="分组名称：" prop="name">
          <el-input v-model="groupForm.name" placeholder="请输入分组名称"></el-input>
        </el-form-item>
        <el-form-item label="所属上级：" prop="parent_id">
          <el-select v-model="groupForm.parent_id" placeholder="请选择" style="width: 100%;">
            <el-option label="顶层分组" :value="0"></el-option>
            <el-option v-for="item in groupTree" :key="item.id" :label="item.label" :value="item.id"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitGroupForm">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getGroups, createGroup, updateGroup, deleteGroup, getGroupDevices, removeDevicesFromGroup } from '@/api/device'

export default {
  name: 'GroupList',
  data() {
    return {
      groupSearch: '',
      deviceSearch: '',
      currentGroupId: null,
      groupTree: [],
      defaultProps: {
        children: 'children',
        label: 'label'
      },
      groupDevices: [],
      selectedDevices: [],
      total: 0,
      pageSize: 10,
      currentPage: 1,
      loading: false,
      
      // 弹窗相关
      dialogVisible: false,
      dialogTitle: '新增分组',
      groupForm: {
        id: null,
        name: '',
        parentId: '0'
      },
      groupRules: {
        name: [{ required: true, message: '请输入分组名称', trigger: 'blur' }],
        parentId: [{ required: true, message: '请选择所属上级', trigger: 'change' }]
      }
    }
  },
  mounted() {
    this.fetchGroupTree()
    // 默认加载第一个分组的设备
    this.$nextTick(() => {
      if (this.groupTree.length > 0) {
        this.currentGroupId = this.groupTree[0].id
        this.fetchGroupDevices()
      }
    })
  },
  methods: {
    async fetchGroupTree() {
      try {
        const res = await getGroups()
        this.groupTree = res.data || []
      } catch (error) {
        console.error('加载分组失败:', error)
        this.$message.error('加载分组失败')
      }
    },
    async fetchGroupDevices() {
      if (!this.currentGroupId) return
      this.loading = true
      try {
        const res = await getGroupDevices(this.currentGroupId, {
          search: this.deviceSearch,
          page: this.currentPage,
          page_size: this.pageSize
        })
        this.groupDevices = res.data.list || []
        this.total = res.data.total || 0
      } catch (error) {
        console.error('加载设备失败:', error)
      } finally {
        this.loading = false
      }
    },
    handleNodeClick(data) {
      this.currentGroupId = data.id
      this.currentPage = 1
      this.fetchGroupDevices()
    },
    handleSearch() {
      this.currentPage = 1
      this.fetchGroupDevices()
    },
    handleAddGroup() {
      this.dialogTitle = '新增分组'
      this.groupForm = { id: null, name: '', parent_id: 0 }
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs.groupForm.clearValidate()
      })
    },
    handleEditGroup(data) {
      this.dialogTitle = '编辑分组'
      this.groupForm = { id: data.id, name: data.label, parent_id: data.parent_id || 0 }
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs.groupForm.clearValidate()
      })
    },
    handleDeleteGroup(node, data) {
      this.$confirm(`确认删除分组 "${data.label}" 吗?`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await deleteGroup(data.id)
          this.$message.success('删除成功')
          this.fetchGroupTree()
        } catch (error) {
          console.error('删除失败:', error)
          this.$message.error(error.response?.data?.detail || '删除失败')
        }
      }).catch(() => {})
    },
    submitGroupForm() {
      this.$refs.groupForm.validate(async (valid) => {
        if (valid) {
          try {
            if (this.groupForm.id) {
              await updateGroup(this.groupForm.id, {
                name: this.groupForm.name,
                parent_id: this.groupForm.parent_id
              })
              this.$message.success('更新成功')
            } else {
              await createGroup({
                name: this.groupForm.name,
                parent_id: this.groupForm.parent_id
              })
              this.$message.success('新增成功')
            }
            this.dialogVisible = false
            this.fetchGroupTree()
          } catch (error) {
            console.error('保存失败:', error)
            this.$message.error(error.response?.data?.detail || '保存失败')
          }
        }
      })
    },
    handleSelectionChange(val) {
      this.selectedDevices = val
    },
    async handleRemoveDevice(row) {
      this.$confirm('确定要移出该设备吗?', '提示', {
        type: 'warning'
      }).then(async () => {
        try {
          await removeDevicesFromGroup(this.currentGroupId, [row.id])
          this.$message.success('移出成功')
          this.fetchGroupDevices()
        } catch (error) {
          console.error('移出失败:', error)
          this.$message.error('移出失败')
        }
      }).catch(() => {})
    },
    async handleBatchRemove() {
      if (this.selectedDevices.length === 0) {
        this.$message.warning('请选择要移出的设备')
        return
      }
      this.$confirm(`确定要移出选中的${this.selectedDevices.length}个设备吗?`, '提示', {
        type: 'warning'
      }).then(async () => {
        try {
          await removeDevicesFromGroup(this.currentGroupId, this.selectedDevices.map(d => d.id))
          this.$message.success('移出成功')
          this.fetchGroupDevices()
        } catch (error) {
          console.error('移出失败:', error)
          this.$message.error('移出失败')
        }
      }).catch(() => {})
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
      this.fetchGroupDevices()
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.fetchGroupDevices()
    }
  }
}
</script>

<style scoped>
.status-online {
  color: #67c23a;
}
.status-offline {
  color: #909399;
}
.text-danger {
  color: #F56C6C;
}

/* 树节点自定义样式 */
.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}

.tree-actions {
  display: none;
}

.custom-tree-node:hover .tree-actions {
  display: inline-block;
}

.tree-actions i {
  margin-left: 8px;
  color: #409EFF;
  font-size: 14px;
}

.tree-actions i:last-child {
  color: #F56C6C;
}
</style>
