/* ============================================================
   FLIPKART - সম্পূর্ণ জাভাস্ক্রিপ্ট ফাইল (কার্ট ব্যাজ + উইশলিস্ট ফিক্স সহ)
   ============================================================ */

// ============================================================
// 1. পেজ লোডার
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    const loader = document.getElementById('page-loader');
    if (loader) {
        setTimeout(function() {
            loader.classList.add('hidden');
        }, 800);
    }
});

// ============================================================
// 2. টোস্ট নোটিফিকেশন - আপডেটেড (Error Message Clean)
// ============================================================
function showToast(message, type = 'info') {
    const container = document.getElementById('fk-toast-container');
    if (!container) {
        const newContainer = document.createElement('div');
        newContainer.id = 'fk-toast-container';
        document.body.appendChild(newContainer);
    }
    
    const toastContainer = document.getElementById('fk-toast-container');
    const toast = document.createElement('div');
    toast.className = `fk-toast ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle',
        warning: 'fa-exclamation-triangle'
    };
    
    // ✅ Error message clean kore show korbe
    let cleanMessage = message;
    if (type === 'error' && message.includes('duplicate key')) {
        cleanMessage = '❌ Already in wishlist!';
    }
    
    toast.innerHTML = `
        <span class="toast-icon"><i class="fas ${icons[type] || icons.info}"></i></span>
        <span class="toast-msg">${cleanMessage}</span>
        <button class="toast-close">&times;</button>
    `;
    
    toastContainer.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    
    toast.querySelector('.toast-close').addEventListener('click', function() {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    });
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4500);
}

// ============================================================
// 3. কার্ট কাউন্ট আপডেট
// ============================================================
function updateCartCount(count) {
    document.querySelectorAll('.cart-badge, .nav-badge').forEach(el => {
        if (el.closest('a[href*="cart"]') || el.closest('.cart-icon')) {
            if (count > 0) {
                el.textContent = count;
                el.style.display = 'inline-block';
                el.style.animation = 'badgePop 0.4s ease';
            } else {
                el.style.display = 'none';
            }
        }
    });
}

// ============================================================
// 4. উইশলিস্ট কাউন্ট আপডেট
// ============================================================
function updateWishlistCount(count) {
    document.querySelectorAll('.badge-icon, .nav-badge').forEach(el => {
        if (el.closest('a[href*="wishlist"]')) {
            if (count > 0) {
                el.textContent = count;
                el.style.display = 'inline-block';
            } else {
                el.style.display = 'none';
            }
        }
    });
}

// ============================================================
// 5. অ্যালার্ট অটো ডিসমিস
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        document.querySelectorAll('.alert').forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            setTimeout(() => bsAlert.close(), 500);
        });
    }, 5000);
});

// ============================================================
// 6. স্ক্রল টু টপ বাটন
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('scrollTopBtn');
    if (btn) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 400) {
                btn.classList.add('show');
            } else {
                btn.classList.remove('show');
            }
        });
        
        btn.addEventListener('click', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
});

// ============================================================
// 7. পাসওয়ার্ড টগল
// ============================================================
function togglePassword(inputId, iconId) {
    const passwordInput = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        passwordInput.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

// ============================================================
// 8. পাসওয়ার্ড স্ট্রেংথ চেকার
// ============================================================
function checkPasswordStrength(password) {
    let score = 0;
    let color = '#dc3545';
    let text = 'Weak';
    let width = 20;
    
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;
    
    if (score <= 1) { width = 20; color = '#dc3545'; text = 'Weak'; }
    else if (score === 2) { width = 40; color = '#ffc107'; text = 'Fair'; }
    else if (score === 3) { width = 60; color = '#17a2b8'; text = 'Good'; }
    else if (score === 4) { width = 80; color = '#28a745'; text = 'Strong'; }
    else if (score >= 5) { width = 100; color = '#28a745'; text = 'Very Strong'; }
    
    return { width, color, text };
}

// ============================================================
// 9. পেমেন্ট মেথড সিলেক্ট
// ============================================================
function selectPayment(element, value) {
    document.querySelectorAll('.payment-option').forEach(opt => {
        opt.classList.remove('active');
        opt.style.borderColor = 'var(--border-gray)';
        opt.style.borderWidth = '1px';
        opt.style.background = 'var(--white)';
        opt.style.transform = 'none';
        opt.style.boxShadow = 'none';
    });
    
    element.classList.add('active');
    element.style.borderColor = 'var(--primary-blue)';
    element.style.borderWidth = '2px';
    element.style.background = '#f0f7ff';
    element.style.transform = 'translateY(-2px)';
    element.style.boxShadow = 'var(--shadow-sm)';
    
    const radio = element.querySelector('input[type="radio"]');
    if (radio) {
        radio.checked = true;
    }
}

// ============================================================
// 10. ইমেজ প্রিভিউ
// ============================================================
function previewImage(input, previewId) {
    const file = input.files[0];
    const preview = document.getElementById(previewId);
    
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.classList.remove('d-none');
        }
        reader.readAsDataURL(file);
    } else {
        preview.classList.add('d-none');
    }
}

// ============================================================
// 11. এড টু কার্ট AJAX - আপডেটেড
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const form = this.closest('form');
            if (!form) return;
            
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>';
            this.disabled = true;
            
            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new FormData(form)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('✅ Product added to cart!', 'success');
                    updateCartCount(data.cart_count);
                    // ✅ রিফ্রেশ কার্ট ব্যাজ
                    setTimeout(refreshCartBadge, 500);
                } else {
                    showToast(data.message || '❌ Failed to add to cart', 'error');
                }
            })
            .catch(() => {
                showToast('❌ Something went wrong', 'error');
            })
            .finally(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            });
        });
    });
});

// ============================================================
// 12. উইশলিস্ট টগল (AJAX) - আপডেটেড
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.fk-wishlist-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const productId = this.getAttribute('data-product-id');
            const button = this;
            const icon = button.querySelector('.wishlist-icon i');
            const text = button.querySelector('.wishlist-text');
            const tooltip = button.querySelector('.tooltip-text');
            
            button.classList.add('loading');
            const originalHTML = button.innerHTML;
            
            fetch(`/wishlist/toggle/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const inWishlist = data.in_wishlist;
                    const wishlistCount = data.wishlist_count || 0;
                    
                    if (inWishlist) {
                        button.classList.add('active');
                        icon.className = 'fas fa-heart';
                        text.textContent = 'Saved';
                        if (tooltip) tooltip.textContent = 'Remove from wishlist';
                        button.title = 'Remove from wishlist';
                        button.setAttribute('data-in-wishlist', 'true');
                        icon.classList.add('pop');
                        setTimeout(() => icon.classList.remove('pop'), 500);
                        showToast('❤️ Added to wishlist!', 'success');
                    } else {
                        button.classList.remove('active');
                        icon.className = 'far fa-heart';
                        text.textContent = 'Wishlist';
                        if (tooltip) tooltip.textContent = 'Add to wishlist';
                        button.title = 'Add to wishlist';
                        button.setAttribute('data-in-wishlist', 'false');
                        showToast('💔 Removed from wishlist', 'info');
                    }
                    
                    updateWishlistCount(wishlistCount);
                } else {
                    showToast(data.message || '❌ Something went wrong', 'error');
                }
            })
            .catch(() => {
                showToast('❌ Failed to update wishlist', 'error');
            })
            .finally(() => {
                button.classList.remove('loading');
                button.disabled = false;
            });
        });
    });
});

// ============================================================
// 13. কুপন কপি
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.copy-coupon').forEach(button => {
        button.addEventListener('click', function() {
            const code = this.getAttribute('data-code');
            if (!code) return;
            
            navigator.clipboard.writeText(code).then(() => {
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check me-1"></i> Copied!';
                this.classList.remove('btn-outline-secondary');
                this.classList.add('btn-success');
                
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.classList.remove('btn-success');
                    this.classList.add('btn-outline-secondary');
                }, 2000);
            }).catch(() => {
                const textArea = document.createElement('textarea');
                textArea.value = code;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check me-1"></i> Copied!';
                this.classList.remove('btn-outline-secondary');
                this.classList.add('btn-success');
                
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.classList.remove('btn-success');
                    this.classList.add('btn-outline-secondary');
                }, 2000);
            });
        });
    });
});

// ============================================================
// 14. কুপন অ্যাপ্লাই
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    const couponForm = document.getElementById('coupon-form');
    if (couponForm) {
        couponForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const couponCode = document.getElementById('coupon-code');
            if (!couponCode) return;
            
            const code = couponCode.value.trim();
            const applyBtn = document.getElementById('apply-coupon-btn');
            const messageEl = document.getElementById('coupon-message');
            
            if (!code) {
                if (messageEl) {
                    messageEl.innerHTML = '<span class="text-danger"><i class="fas fa-exclamation-circle me-1"></i> Please enter a coupon code</span>';
                }
                showToast('Please enter coupon code', 'error');
                return;
            }
            
            applyBtn.disabled = true;
            applyBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Applying...';
            if (messageEl) messageEl.innerHTML = '';
            
            fetch('/coupons/apply/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `coupon_code=${encodeURIComponent(code)}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (messageEl) {
                        messageEl.innerHTML = `<span class="text-success"><i class="fas fa-check-circle me-1"></i> ${data.message}</span>`;
                    }
                    showToast('✅ Coupon applied!', 'success');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    if (messageEl) {
                        messageEl.innerHTML = `<span class="text-danger"><i class="fas fa-exclamation-circle me-1"></i> ${data.message}</span>`;
                    }
                    showToast(data.message || '❌ Invalid coupon', 'error');
                }
            })
            .catch(() => {
                if (messageEl) {
                    messageEl.innerHTML = '<span class="text-danger"><i class="fas fa-exclamation-circle me-1"></i> Something went wrong</span>';
                }
                showToast('❌ Something went wrong', 'error');
            })
            .finally(() => {
                applyBtn.disabled = false;
                applyBtn.innerHTML = '<i class="fas fa-check me-1"></i> Apply Coupon';
            });
        });
    }
});

// ============================================================
// 15. কুপন রিমুভ
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    const removeBtn = document.getElementById('remove-coupon');
    if (removeBtn) {
        removeBtn.addEventListener('click', function() {
            fetch('/coupons/remove/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Coupon removed', 'info');
                    setTimeout(() => location.reload(), 500);
                }
            });
        });
    }
});

// ============================================================
// 16. সিএসআরএফ টোকেন হেল্পার
// ============================================================
function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    if (token) return token.value;
    
    const cookieToken = document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken='));
    if (cookieToken) return cookieToken.split('=')[1];
    
    return '';
}

// ============================================================
// 17. ফর্ম ভ্যালিডেশন
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = '#dc3545';
                    isValid = false;
                } else {
                    field.style.borderColor = 'var(--border-gray)';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showToast('Please fill in all required fields', 'error');
            }
        });
    });
});

// ============================================================
// 18. ইনপুট ফোকাস/ব্লার ইফেক্ট
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.form-control, .form-select').forEach(input => {
        input.addEventListener('focus', function() {
            this.style.borderColor = 'var(--primary-blue)';
        });
        input.addEventListener('blur', function() {
            if (!this.value.trim()) {
                this.style.borderColor = 'var(--border-gray)';
            }
        });
    });
});

// ============================================================
// ✅ 19. কার্ট ব্যাজ - রিয়েল-টাইম আপডেট (নতুন)
// ============================================================
function updateCartBadge(count) {
    const desktopBadge = document.getElementById('cart-badge-desktop');
    if (desktopBadge) {
        if (count > 0) {
            desktopBadge.textContent = count;
            desktopBadge.style.display = 'inline-block';
            desktopBadge.style.animation = 'badgePop 0.4s ease';
        } else {
            desktopBadge.textContent = '0';
            desktopBadge.style.display = 'none';
        }
    }
    
    const mobileBadge = document.getElementById('cart-badge-mobile');
    if (mobileBadge) {
        if (count > 0) {
            mobileBadge.textContent = count;
            mobileBadge.style.display = 'inline-block';
            mobileBadge.style.animation = 'badgePop 0.4s ease';
        } else {
            mobileBadge.textContent = '0';
            mobileBadge.style.display = 'none';
        }
    }
    
    const dot = document.getElementById('mobile-cart-dot');
    if (dot) {
        dot.style.display = count > 0 ? 'block' : 'none';
    }
}

// ============================================================
// ✅ 20. সার্ভার থেকে কার্ট কাউন্ট রিফ্রেশ (নতুন)
// ============================================================
function refreshCartBadge() {
    fetch('/cart/api/count/')
        .then(response => response.json())
        .then(data => {
            if (data.count !== undefined) {
                updateCartBadge(data.count);
            }
        })
        .catch(error => {
            console.log('⚠️ Cart count refresh error:', error);
        });
}

// ============================================================
// ✅ 21. উইশলিস্ট ব্যাজ - রিয়েল-টাইম আপডেট (নতুন)
// ============================================================
function updateWishlistBadge(count) {
    const badge = document.getElementById('wishlist-badge-desktop');
    if (badge) {
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline-block';
        } else {
            badge.textContent = '0';
            badge.style.display = 'none';
        }
    }
}

// ============================================================
// ✅ 22. সার্ভার থেকে উইশলিস্ট কাউন্ট রিফ্রেশ (নতুন)
// ============================================================
function refreshWishlistBadge() {
    fetch('/wishlist/api/count/')
        .then(response => response.json())
        .then(data => {
            if (data.count !== undefined) {
                updateWishlistBadge(data.count);
            }
        })
        .catch(error => {
            console.log('⚠️ Wishlist count refresh error:', error);
        });
}

// ============================================================
// ✅ 23. AJAX - কার্টে আইটেম যোগ করুন (নতুন)
// ============================================================
function addToCartAjax(productId, quantity = 1) {
    fetch('/cart/api/add/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `product_id=${productId}&quantity=${quantity}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            updateCartBadge(data.cart_total_items);
            setTimeout(refreshCartBadge, 500);
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(() => {
        showToast('❌ Something went wrong!', 'error');
    });
}

// ============================================================
// ✅ 24. AJAX - উইশলিস্ট টগল (নতুন)
// ============================================================
function toggleWishlistAjax(productId) {
    fetch(`/wishlist/api/toggle/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, data.in_wishlist ? 'success' : 'info');
            updateWishlistBadge(data.wishlist_count);
            
            const btn = document.querySelector(`.wishlist-btn[data-product-id="${productId}"]`);
            if (btn) {
                if (data.in_wishlist) {
                    btn.classList.add('active');
                    btn.innerHTML = '<i class="fas fa-heart text-danger"></i>';
                } else {
                    btn.classList.remove('active');
                    btn.innerHTML = '<i class="far fa-heart"></i>';
                }
            }
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(() => {
        showToast('❌ Something went wrong!', 'error');
    });
}

// ============================================================
// ✅ 25. DOM Ready - সবকিছু সেটআপ (আপডেটেড)
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    // Initial load
    refreshCartBadge();
    refreshWishlistBadge();
    
    // পেজ ভিজিবল হলে আপডেট
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            refreshCartBadge();
            refreshWishlistBadge();
        }
    });
    
    // প্রতি ৩০ সেকেন্ডে আপডেট
    setInterval(refreshCartBadge, 30000);
    setInterval(refreshWishlistBadge, 30000);
    
    // AJAX Add to Cart
    document.querySelectorAll('.add-to-cart-ajax').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            const quantity = parseInt(this.dataset.quantity || 1);
            addToCartAjax(productId, quantity);
        });
    });
    
    // AJAX Wishlist Toggle
    document.querySelectorAll('.wishlist-toggle-ajax, .wishlist-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            if (productId) {
                toggleWishlistAjax(productId);
            }
        });
    });
    
    // কার্ট বাটন ক্লিক করলে ব্যাজ রিফ্রেশ
    document.addEventListener('click', function(e) {
        const addToCartBtn = e.target.closest('.add-to-cart-btn, .fk-product-card .btn-primary');
        if (addToCartBtn) {
            setTimeout(refreshCartBadge, 1000);
        }
    });
});

// ============================================================
// 26. ব্রাউজার ব্যাক/ফরওয়ার্ডে লোডার হাইড
// ============================================================
window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        const loader = document.getElementById('fkLoader');
        if (loader) {
            loader.classList.add('fade-out');
            setTimeout(function() {
                loader.style.display = 'none';
            }, 500);
        }
    }
});

// ============================================================
// কার্ট ব্যাজ - রিয়েল-টাইম আপডেট
// ============================================================

function updateCartBadge(count) {
    const desktopBadge = document.getElementById('cart-badge-desktop');
    if (desktopBadge) {
        if (count > 0) {
            desktopBadge.textContent = count;
            desktopBadge.style.display = 'inline-block';
            desktopBadge.style.animation = 'badgePop 0.4s ease';
        } else {
            desktopBadge.textContent = '0';
            desktopBadge.style.display = 'none';
        }
    }
    
    const mobileBadge = document.getElementById('cart-badge-mobile');
    if (mobileBadge) {
        if (count > 0) {
            mobileBadge.textContent = count;
            mobileBadge.style.display = 'inline-block';
            mobileBadge.style.animation = 'badgePop 0.4s ease';
        } else {
            mobileBadge.textContent = '0';
            mobileBadge.style.display = 'none';
        }
    }
    
    const dot = document.getElementById('mobile-cart-dot');
    if (dot) {
        dot.style.display = count > 0 ? 'block' : 'none';
    }
}

function refreshCartBadge() {
    fetch('/cart/api/count/')
        .then(response => response.json())
        .then(data => {
            if (data.count !== undefined) {
                updateCartBadge(data.count);
            }
        })
        .catch(() => {});
}
// ============================================================
// 27. কনসোল মেসেজ
// ============================================================
console.log('🚀 Flipkart Style Loaded!');
console.log('💡 Tip: showToast("Message", "success|error|info|warning")');
console.log('💡 Tip: updateCartCount(5) - Update cart badge');
console.log('💡 Tip: updateWishlistCount(3) - Update wishlist badge');
console.log('💡 Tip: togglePassword("inputId", "iconId") - Toggle password visibility');
console.log('💡 Tip: selectPayment(element, "cod") - Select payment method');
console.log('✅ Real-time Cart Badge Active');
console.log('✅ Real-time Wishlist Badge Active');