document.addEventListener('DOMContentLoaded', function() {
    const paymentOptions = document.querySelectorAll('.payment-option');
    const qrcodeContainer = document.querySelector('.payment-qrcode');
    const stripeForm = document.querySelector('.stripe-form');
    const qrcodeImg = document.querySelector('#qrcode');
    let selectedMethod = null;

    // 初始化Stripe
    const stripe = Stripe('your_stripe_public_key');
    const elements = stripe.elements();
    const card = elements.create('card');
    card.mount('#stripe-card-element');

    // 获取计划ID
    const urlParams = new URLSearchParams(window.location.search);
    const planId = urlParams.get('plan');

    // 支付方式选择
    paymentOptions.forEach(option => {
        option.addEventListener('click', async () => {
            const method = option.dataset.method;
            selectedMethod = method;

            // 移除其他选项的选中状态
            paymentOptions.forEach(opt => opt.classList.remove('selected'));
            option.classList.add('selected');

            try {
                // 创建支付订单
                const response = await fetch('/payment/create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        method: method,
                        plan_id: planId
                    })
                });

                if (!response.ok) {
                    throw new Error('支付创建失败');
                }

                const paymentData = await response.json();

            // 根据支付方式显示不同的支付界面
            if (paymentData.type === 'qrcode') {
                qrcodeImg.src = paymentData.data;
                qrcodeContainer.classList.remove('hidden');
                stripeForm.classList.add('hidden');
                startPollingOrderStatus();
            } else if (paymentData.type === 'stripe') {
                stripeForm.classList.remove('hidden');
                qrcodeContainer.classList.add('hidden');
                handleStripePayment(paymentData.client_secret);
            }
        });
    });

    // 处理Stripe支付
    async function handleStripePayment(clientSecret) {
        const stripeSubmit = document.querySelector('#stripe-submit');
        stripeSubmit.addEventListener('click', async () => {
            const result = await stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: card
                }
            });

            if (result.error) {
                alert(result.error.message);
            } else {
                window.location.href = '/user/orders';
            }
        });
    }

    // 轮询订单状态
    async function startPollingOrderStatus() {
        const orderId = new URLSearchParams(window.location.search).get('order_id');
        const interval = setInterval(async () => {
            const response = await fetch(`/payment/status/${orderId}`);
            const data = await response.json();
            
            if (data.status === 'paid') {
                clearInterval(interval);
                window.location.href = '/user/orders';
            }
        }, 3000);
    }

    // 取消支付
    document.querySelector('.cancel-payment')?.addEventListener('click', () => {
        qrcodeContainer.classList.add('hidden');
        stripeForm.classList.add('hidden');
        paymentOptions.forEach(opt => opt.classList.remove('selected'));
    });
});