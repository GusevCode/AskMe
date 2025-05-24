$(document).ready(function() {
    // Получаем CSRF токен из мета-тега
    const csrfToken = $('meta[name=csrf-token]').attr('content');
    
    // Настройка AJAX для отправки CSRF токена
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            }
        }
    });
    
    // Функция для проверки безопасных HTTP методов
    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    
    // Лайки вопросов
    $('.vote-btn').click(function(e) {
        e.preventDefault();
        
        const button = $(this);
        const questionId = button.data('question-id');
        const voteType = button.data('vote-type');
        
        // Сохраняем исходное состояние кнопки
        const wasActive = (voteType === 'like' && button.hasClass('btn-success')) || 
                         (voteType === 'dislike' && button.hasClass('btn-danger'));
        
        // Блокируем кнопку на время запроса
        button.prop('disabled', true);
        
        $.ajax({
            url: '/ajax/vote-question/',
            method: 'POST',
            data: {
                'question_id': questionId,
                'vote_type': voteType,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response) {
                if (response.success) {
                    // Обновляем рейтинг
                    $('.rating-value[data-question-id="' + questionId + '"]').text(response.new_rating);
                    
                    // Получаем кнопки
                    const likeBtn = $('.vote-btn[data-question-id="' + questionId + '"][data-vote-type="like"]');
                    const dislikeBtn = $('.vote-btn[data-question-id="' + questionId + '"][data-vote-type="dislike"]');
                    
                    // Сбрасываем все кнопки к исходному состоянию
                    likeBtn.removeClass('btn-success').addClass('btn-outline-success');
                    dislikeBtn.removeClass('btn-danger').addClass('btn-outline-danger');
                    
                    // Если кнопка была неактивна, активируем её (новый голос)
                    if (!wasActive) {
                        if (voteType === 'like') {
                            button.removeClass('btn-outline-success').addClass('btn-success');
                        } else if (voteType === 'dislike') {
                            button.removeClass('btn-outline-danger').addClass('btn-danger');
                        }
                    }
                    // Если кнопка была активна, она остается в исходном состоянии (отмена голоса)
                }
            },
            error: function(xhr) {
                console.error('Vote error:', xhr.responseJSON);
                alert('Error voting. Please try again.');
            },
            complete: function() {
                // Разблокируем кнопку
                button.prop('disabled', false);
            }
        });
    });
    
    // Лайки ответов
    $('.vote-answer-btn').click(function(e) {
        e.preventDefault();
        
        const button = $(this);
        const answerId = button.data('answer-id');
        const voteType = button.data('vote-type');
        
        // Сохраняем исходное состояние кнопки
        const wasActive = (voteType === 'like' && button.hasClass('btn-success')) || 
                         (voteType === 'dislike' && button.hasClass('btn-danger'));
        
        // Блокируем кнопку на время запроса
        button.prop('disabled', true);
        
        $.ajax({
            url: '/ajax/vote-answer/',
            method: 'POST',
            data: {
                'answer_id': answerId,
                'vote_type': voteType,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response) {
                if (response.success) {
                    // Обновляем рейтинг
                    $('.answer-rating-value[data-answer-id="' + answerId + '"]').text(response.new_rating);
                    
                    // Получаем кнопки
                    const likeBtn = $('.vote-answer-btn[data-answer-id="' + answerId + '"][data-vote-type="like"]');
                    const dislikeBtn = $('.vote-answer-btn[data-answer-id="' + answerId + '"][data-vote-type="dislike"]');
                    
                    // Сбрасываем все кнопки к исходному состоянию
                    likeBtn.removeClass('btn-success').addClass('btn-outline-success');
                    dislikeBtn.removeClass('btn-danger').addClass('btn-outline-danger');
                    
                    // Если кнопка была неактивна, активируем её (новый голос)
                    if (!wasActive) {
                        if (voteType === 'like') {
                            button.removeClass('btn-outline-success').addClass('btn-success');
                        } else if (voteType === 'dislike') {
                            button.removeClass('btn-outline-danger').addClass('btn-danger');
                        }
                    }
                    // Если кнопка была активна, она остается в исходном состоянии (отмена голоса)
                }
            },
            error: function(xhr) {
                console.error('Vote error:', xhr.responseJSON);
                alert('Error voting. Please try again.');
            },
            complete: function() {
                // Разблокируем кнопку
                button.prop('disabled', false);
            }
        });
    });
    
    // Отметка правильного ответа
    $('.correct-answer-checkbox').change(function() {
        const checkbox = $(this);
        const answerId = checkbox.data('answer-id');
        
        // Блокируем чекбокс на время запроса
        checkbox.prop('disabled', true);
        
        $.ajax({
            url: '/ajax/mark-correct/',
            method: 'POST',
            data: {
                'answer_id': answerId,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response) {
                if (response.success) {
                    // Если ответ стал правильным, снимаем галочки с других ответов
                    if (response.is_correct) {
                        $('.correct-answer-checkbox').not(checkbox).prop('checked', false);
                    }
                    
                    // Устанавливаем состояние текущего чекбокса
                    checkbox.prop('checked', response.is_correct);
                }
            },
            error: function(xhr) {
                console.error('Mark correct error:', xhr.responseJSON);
                alert('Error marking answer. Please try again.');
                // Возвращаем чекбокс в исходное состояние
                checkbox.prop('checked', !checkbox.prop('checked'));
            },
            complete: function() {
                // Разблокируем чекбокс
                checkbox.prop('disabled', false);
            }
        });
    });
}); 