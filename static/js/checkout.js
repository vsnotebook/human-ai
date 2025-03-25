document.addEventListener('DOMContentLoaded', function() {
    const paymentOptions = document.querySelectorAll('.payment-option');
    const overlay = document.querySelector('.payment-overlay');
    const qrcodeLarge = document.querySelector('#payment-qrcode-large');
    const closeModal = document.querySelector('.close-modal');
    const paymentResult = document.querySelector('#payment-result');
    let paymentInterval;

    // 支付方式选择
    paymentOptions.forEach(option => {
        option.addEventListener('click', async () => {
            const method = option.dataset.method;

            try {
                const response = await fetch('/payment/create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        method: method,
                        plan_id: new URLSearchParams(window.location.search).get('plan')
                    })
                });

                if (!response.ok) {
                    throw new Error('支付创建失败');
                }

                const paymentData = await response.json();
                
                // 显示支付二维码
                qrcodeLarge.src = paymentData.qr_code;
                overlay.style.display = 'flex';
                
                // 开始轮询支付状态
                startPollingOrderStatus(paymentData.order_id);
            } catch (error) {
                alert('创建支付订单失败：' + error.message);
            }
        });
    });

    // 关闭弹窗
    closeModal.addEventListener('click', () => {
        overlay.style.display = 'none';
        if (paymentInterval) {
            clearInterval(paymentInterval);
        }
    });

    // 轮询订单状态
    function startPollingOrderStatus(orderId) {
        if (paymentInterval) {
            clearInterval(paymentInterval);
        }

        paymentInterval = setInterval(async () => {
            try {
                const response = await fetch(`/payment/status/${orderId}`);
                const data = await response.json();
                
                if (data.status === 'paid') {
                    paymentResult.textContent = '支付成功！正在跳转...';
                    clearInterval(paymentInterval);
                    setTimeout(() => {
                        window.location.href = '/user/subscriptions';
                    }, 2000);
                }
            } catch (error) {
                console.error('检查支付状态失败：', error);
            }
        }, 3000);
    }
});