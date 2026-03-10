import Vue from 'vue'
import Vuex from 'vuex'
import { getUnreadCount } from '@/api/message'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    unreadCount: 0
  },
  mutations: {
    SET_UNREAD_COUNT(state, count) {
      state.unreadCount = count
    }
  },
  actions: {
    async fetchUnreadCount({ commit }) {
      try {
        const res = await getUnreadCount()
        commit('SET_UNREAD_COUNT', res.data.count)
      } catch (error) {
        console.error('获取未读消息数量失败:', error)
      }
    }
  },
  getters: {
    unreadCount: state => state.unreadCount
  }
})
