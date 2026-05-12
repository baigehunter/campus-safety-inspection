// 微信订阅消息 —— 踩了不少坑，记录一下免得忘了：
// wx.requestSubscribeMessage 这个 API 有个很恶心的限制，
// 必须在用户点击手势的回调链里直接调用，不能用 setTimeout/await 打断。
// 所以流程是：先拿模板ID → 弹 modal → 在 confirm 回调里调订阅弹窗，
// 这样 confirm 回调算一次新的 tap 手势，刚好满足要求。
import { api } from './request'

export async function requestSubscribe(categories: string[]): Promise<void> {
  // #ifdef MP-WEIXIN
  let templates: Record<string, string> = {}
  try {
    templates = (await api.getWxTemplates()) as Record<string, string>
  } catch (e) {
    console.log('获取模板列表失败:', e)
    return
  }

  // 把传入的类别名映射成微信的模板ID
  const tmplIds: string[] = []
  for (const cat of categories) {
    const tplId = templates[cat]
    if (tplId) {
      tmplIds.push(tplId)
    }
  }
  if (tmplIds.length === 0) return

  // 这里弹出 modal 是关键——点了"去开启"之后的新回调是一个新鲜手势，
  // 微信才允许在这个回调链里弹出订阅弹窗
  uni.showModal({
    title: '开启消息通知',
    content: '建议开启通知，以便实时接收巡检异常、整改任务等重要消息。',
    confirmText: '去开启',
    cancelText: '暂不',
    success: (modalRes) => {
      if (!modalRes.confirm) return

      uni.requestSubscribeMessage({
        tmplIds,
        success: (subRes: any) => {
          // 把用户勾选的模板整理出来，同步到后端
          const accepted: string[] = []
          for (const cat of categories) {
            const tplId = templates[cat]
            if (tplId && subRes[tplId] === 'accept') {
              accepted.push(cat)
            }
          }
          if (accepted.length > 0) {
            // 上传失败也无所谓，下次再补
            api.updateSubscribe(accepted).catch(() => {})
          }
        },
        fail: (err: any) => {
          console.log('订阅消息: 用户取消或失败', err)
        }
      })
    }
  })
  // #endif
}
