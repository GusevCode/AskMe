$(document).ready(function() {
    const csrfToken = $('meta[name=csrf-token]').attr('content');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            }
        }
    });

    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    // Функция для показа Toast уведомлений
    function showToast(message, type = 'info') {
        const toastContainer = $('.toast-container');
        if (toastContainer.length === 0) {
            $('body').append('<div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 9999;"></div>');
        }
        
        let iconColor = 'info';
        let title = 'Уведомление';
        
        switch(type) {
            case 'success':
                iconColor = 'success';
                title = 'Успех';
                break;
            case 'error':
                iconColor = 'danger';
                title = 'Ошибка';
                break;
            case 'warning':
                iconColor = 'warning';
                title = 'Предупреждение';
                break;
        }
        
        const toastHtml = `
            <div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-bs-autohide="true" data-bs-delay="5000">
                <div class="toast-header">
                    <div class="rounded me-2 bg-${iconColor}" style="width: 20px; height: 20px;"></div>
                    <strong class="me-auto">${title}</strong>
                    <small class="text-muted">только что</small>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        const $toast = $(toastHtml);
        $('.toast-container').append($toast);
        
        const toast = new bootstrap.Toast($toast[0], {
            autohide: true,
            delay: 5000
        });
        toast.show();
        
        // Удаляем toast из DOM после скрытия
        $toast[0].addEventListener('hidden.bs.toast', function() {
            $toast.remove();
        });
    }

    $('.vote-btn').click(function(e) {
        e.preventDefault();
        
        const button = $(this);
        const questionId = button.data('question-id');
        const voteType = button.data('vote-type');

        const wasActive = (voteType === 'like' && button.hasClass('btn-success')) || 
                         (voteType === 'dislike' && button.hasClass('btn-danger'));

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
                    $('.rating-value[data-question-id="' + questionId + '"]').text(response.new_rating);

                    const likeBtn = $('.vote-btn[data-question-id="' + questionId + '"][data-vote-type="like"]');
                    const dislikeBtn = $('.vote-btn[data-question-id="' + questionId + '"][data-vote-type="dislike"]');

                    likeBtn.removeClass('btn-success').addClass('btn-outline-success');
                    dislikeBtn.removeClass('btn-danger').addClass('btn-outline-danger');

                    if (!wasActive) {
                        if (voteType === 'like') {
                            button.removeClass('btn-outline-success').addClass('btn-success');
                            showToast('Вы поставили лайк!', 'success');
                        } else if (voteType === 'dislike') {
                            button.removeClass('btn-outline-danger').addClass('btn-danger');
                            showToast('Вы поставили дизлайк!', 'info');
                        }
                    } else {
                        showToast('Голос отменен', 'info');
                    }
                }
            },
            error: function(xhr) {
                console.error('Vote error:', xhr.responseJSON);
                showToast('Ошибка голосования. Попробуйте снова.', 'error');
            },
            complete: function() {
                button.prop('disabled', false);
            }
        });
    });

    $('.vote-answer-btn').click(function(e) {
        e.preventDefault();
        
        const button = $(this);
        const answerId = button.data('answer-id');
        const voteType = button.data('vote-type');

        const wasActive = (voteType === 'like' && button.hasClass('btn-success')) || 
                         (voteType === 'dislike' && button.hasClass('btn-danger'));

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
                    $('.answer-rating-value[data-answer-id="' + answerId + '"]').text(response.new_rating);

                    const likeBtn = $('.vote-answer-btn[data-answer-id="' + answerId + '"][data-vote-type="like"]');
                    const dislikeBtn = $('.vote-answer-btn[data-answer-id="' + answerId + '"][data-vote-type="dislike"]');

                    likeBtn.removeClass('btn-success').addClass('btn-outline-success');
                    dislikeBtn.removeClass('btn-danger').addClass('btn-outline-danger');

                    if (!wasActive) {
                        if (voteType === 'like') {
                            button.removeClass('btn-outline-success').addClass('btn-success');
                            showToast('Вы поставили лайк ответу!', 'success');
                        } else if (voteType === 'dislike') {
                            button.removeClass('btn-outline-danger').addClass('btn-danger');
                            showToast('Вы поставили дизлайк ответу!', 'info');
                        }
                    } else {
                        showToast('Голос за ответ отменен', 'info');
                    }
                }
            },
            error: function(xhr) {
                console.error('Vote error:', xhr.responseJSON);
                showToast('Ошибка голосования за ответ. Попробуйте снова.', 'error');
            },
            complete: function() {
                button.prop('disabled', false);
            }
        });
    });
    
    $('.correct-answer-checkbox').change(function() {
        const checkbox = $(this);
        const answerId = checkbox.data('answer-id');
        
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
                    if (response.is_correct) {
                        $('.correct-answer-checkbox').not(checkbox).prop('checked', false);
                        showToast('Ответ отмечен как правильный!', 'success');
                    } else {
                        showToast('Отметка правильного ответа снята', 'info');
                    }

                    checkbox.prop('checked', response.is_correct);
                }
            },
            error: function(xhr) {
                console.error('Mark correct error:', xhr.responseJSON);
                showToast('Ошибка отметки ответа. Попробуйте снова.', 'error');
                checkbox.prop('checked', !checkbox.prop('checked'));
            },
            complete: function() {
                checkbox.prop('disabled', false);
            }
        });
    });
}); 