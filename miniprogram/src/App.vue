<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";

onLaunch(() => {
  console.log("App Launch");
  checkLoginStatus();
});

onShow(() => {
  console.log("App Show");
});

onHide(() => {
  console.log("App Hide");
});

function checkLoginStatus() {
  const token = uni.getStorageSync('access_token');
  const userInfo = uni.getStorageSync('userInfo');
  if (!token || !userInfo) {
    uni.reLaunch({ url: '/pages/login/index' });
  }
}
</script>

<style>
/* --- CSS Custom Properties --- */
page {
  --color-brand-950: #0a0f1e;
  --color-brand-900: #0f172a;
  --color-brand-800: #1a2744;
  --color-brand-700: #1e3b5c;
  --color-accent: #06b6d4;
  --color-accent-glow: #22d3ee;
  --color-accent-bg: rgba(6, 182, 212, 0.08);
  --color-surface: #ffffff;
  --color-surface-glass: rgba(255, 255, 255, 0.75);
  --color-bg-primary: #f7f8fc;
  --color-bg-secondary: #eef0f6;
  --color-text-primary: #0f172a;
  --color-text-secondary: #334155;
  --color-text-tertiary: #64748b;
  --color-text-muted: #94a3b8;
  --color-text-inverse: #ffffff;
  --color-border-light: #e2e8f0;
  --color-border-strong: #cbd5e1;
  --color-success: #059669;
  --color-success-bg: #ecfdf5;
  --color-warning: #d97706;
  --color-warning-bg: #fffbeb;
  --color-danger: #dc2626;
  --color-danger-bg: #fef2f2;
  --color-info: #2563eb;
  --color-info-bg: #eff6ff;
  --shadow-sm: 0 1rpx 3rpx rgba(15, 23, 42, 0.04);
  --shadow-md: 0 8rpx 30rpx rgba(15, 23, 42, 0.06);
  --shadow-lg: 0 16rpx 48rpx rgba(15, 23, 42, 0.10);
  --shadow-glow: 0 8rpx 32rpx rgba(6, 182, 212, 0.18);
  --radius-sm: 8rpx;
  --radius-md: 14rpx;
  --radius-lg: 20rpx;
  --radius-xl: 24rpx;
  --radius-full: 50%;

  background-color: var(--color-bg-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
  font-size: 32rpx;
  color: var(--color-text-primary);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

/* Animation Keyframes */

/* Fade + Slide Up — primary page entrance */
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(32rpx); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Fade + Slide In From Right — list/card items */
@keyframes fadeSlideRight {
  from { opacity: 0; transform: translateX(24rpx); }
  to   { opacity: 1; transform: translateX(0); }
}

/* Scale Fade — modals, popups, overlays */
@keyframes scaleFadeIn {
  from { opacity: 0; transform: scale(0.92); }
  to   { opacity: 1; transform: scale(1); }
}

/* Slide Up From Bottom — bottom sheet panels */
@keyframes slideUpIn {
  from { transform: translateY(100%); }
  to   { transform: translateY(0); }
}

/* Fade In — masks, simple reveals */
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

/* Shimmer — skeleton loading */
@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Soft Glow Pulse — badges, notification dots */
@keyframes glowPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(6, 182, 212, 0.4); }
  50%      { box-shadow: 0 0 0 8rpx rgba(6, 182, 212, 0); }
}

/* Rotate + Scale In — checkmarks, success icons */
@keyframes rotateIn {
  from { opacity: 0; transform: rotate(-90deg) scale(0.3); }
  to   { opacity: 1; transform: rotate(0deg) scale(1); }
}

/* Slow Drift — background decorative elements */
@keyframes slowDrift {
  0%   { transform: translate(0, 0); }
  50%  { transform: translate(20rpx, -30rpx); }
  100% { transform: translate(-10rpx, 10rpx); }
}

/* Gentle Float — stat cards, profile elements */
@keyframes gentleFloat {
  0%, 100% { transform: translateY(0); }
  50%      { transform: translateY(-6rpx); }
}

/* Utility Classes */

/* Entrance animations */
.anim-fade-up    { animation: fadeSlideUp 0.45s cubic-bezier(0.22, 0.61, 0.36, 1) both; }
.anim-fade-right { animation: fadeSlideRight 0.38s cubic-bezier(0.22, 0.61, 0.36, 1) both; }
.anim-scale-in   { animation: scaleFadeIn 0.32s cubic-bezier(0.34, 1.56, 0.64, 1) both; }
.anim-slide-up   { animation: slideUpIn 0.38s cubic-bezier(0.22, 0.61, 0.36, 1) both; }
.anim-fade-in    { animation: fadeIn 0.28s ease-out both; }
.anim-drift      { animation: slowDrift 10s ease-in-out infinite alternate; }

/* Staggered delays — 8 levels, ~40ms increments */
.delay-1 { animation-delay: 0.00s; }
.delay-2 { animation-delay: 0.05s; }
.delay-3 { animation-delay: 0.10s; }
.delay-4 { animation-delay: 0.15s; }
.delay-5 { animation-delay: 0.20s; }
.delay-6 { animation-delay: 0.25s; }
.delay-7 { animation-delay: 0.30s; }
.delay-8 { animation-delay: 0.35s; }

/* Skeleton loading */
.skeleton {
  background: linear-gradient(90deg, #e8ecf2 25%, #f1f4f8 50%, #e8ecf2 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-sm);
}

.skeleton-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 28rpx;
  margin-bottom: 16rpx;
  box-shadow: var(--shadow-sm);
}

/* Button press feedback */
.btn-press:active {
  transform: scale(0.96);
  transition: transform 0.12s cubic-bezier(0.22, 0.61, 0.36, 1);
}

/* Mask fade transition */
.mask-fade {
  transition: opacity 0.28s ease-out;
}

/* 尊重系统"减少动效"设置，动画全关 */
@media (prefers-reduced-motion: reduce) {
  .anim-fade-up,
  .anim-fade-right,
  .anim-scale-in,
  .anim-slide-up,
  .anim-fade-in {
    animation: none;
    opacity: 1;
    transform: none;
  }
  .skeleton { animation: none; background: #e8ecf2; }
}

/* Reset */
::-webkit-scrollbar { display: none; width: 0; }

button { margin: 0; padding: 0; background: none; border: none; font-family: inherit; }
button::after { border: none; }
</style>
