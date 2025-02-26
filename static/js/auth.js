document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('auth-modal');
    const authTrigger = document.querySelector('.auth-trigger');
    const tabs = document.querySelectorAll('.auth-tab');
    const forms = document.querySelectorAll('.auth-form');

    // Открытие модального окна
    if (authTrigger) {
        authTrigger.addEventListener('click', () => {
            modal.style.display = 'block';
            // Добавляем небольшую задержку для анимации
            setTimeout(() => {
                modal.classList.add('visible');
            }, 10);
        });
    }

    // Закрытие модального окна
    function closeModal() {
        modal.classList.remove('visible');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }

    // Переключение между формами
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const formId = tab.dataset.tab;
            
            tabs.forEach(t => t.classList.remove('active'));
            forms.forEach(f => {
                f.classList.remove('active');
                f.style.display = 'none';
            });
            
            tab.classList.add('active');
            const activeForm = document.getElementById(`${formId}-form`);
            activeForm.style.display = 'block';
            setTimeout(() => {
                activeForm.classList.add('active');
            }, 10);
        });
    });

    // Закрытие по клику вне модального окна
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Обработка форм с анимацией ошибок
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    function showError(form, message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i>${message}`;
        
        const existingError = form.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        
        form.insertBefore(errorDiv, form.firstChild);
        form.classList.add('shake');
        setTimeout(() => {
            form.classList.remove('shake');
        }, 400);
    }

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(loginForm);
        try {
            const response = await fetch('/accounts/login/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });
            
            if (response.ok) {
                window.location.reload();
            } else {
                showError(loginForm, 'Неверное имя пользователя или пароль');
            }
        } catch (error) {
            showError(loginForm, 'Произошла ошибка при входе');
        }
    });

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(registerForm);
        try {
            const response = await fetch('/register/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });
            
            if (response.ok) {
                window.location.reload();
            } else {
                const data = await response.json();
                showError(registerForm, data.error || 'Ошибка регистрации');
            }
        } catch (error) {
            showError(registerForm, 'Произошла ошибка при регистрации');
        }
    });

    // Анимация полей ввода
    document.querySelectorAll('.form-group input').forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', () => {
            input.parentElement.classList.remove('focused');
        });
    });
}); 