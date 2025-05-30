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

    function showToast(message, type = 'info') {
        const toastContainer = $('.toast-container');
        if (toastContainer.length === 0) {
            $('body').append('<div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 9999;"></div>');
        }
        
        let iconColor = 'info';
        let title = 'Notification';
        
        switch(type) {
            case 'success':
                iconColor = 'success';
                title = 'Success';
                break;
            case 'error':
                iconColor = 'danger';
                title = 'Error';
                break;
            case 'warning':
                iconColor = 'warning';
                title = 'Warning';
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
                            showToast('You voted up!', 'success');
                        } else if (voteType === 'dislike') {
                            button.removeClass('btn-outline-danger').addClass('btn-danger');
                            showToast('You voted down!', 'info');
                        }
                    } else {
                        showToast('Vote revert', 'info');
                    }
                }
            },
            error: function(xhr) {
                console.error('Vote error:', xhr.responseJSON);
                showToast('Vote error.', 'error');
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
                            showToast('You voted up answer!', 'success');
                        } else if (voteType === 'dislike') {
                            button.removeClass('btn-outline-danger').addClass('btn-danger');
                            showToast('You voted down answer!', 'info');
                        }
                    } else {
                        showToast('Your vote is revert', 'info');
                    }
                }
            },
            error: function(xhr) {
                console.error('Vote error:', xhr.responseJSON);
                showToast('Vote error.', 'error');
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
                        showToast('Asnwer marked as correct!', 'success');
                    } else {
                        showToast('Answer unmarked as correct!', 'info');
                    }

                    checkbox.prop('checked', response.is_correct);
                }
            },
            error: function(xhr) {
                console.error('Mark correct error:', xhr.responseJSON);
                showToast('Mark correct error.', 'error');
                checkbox.prop('checked', !checkbox.prop('checked'));
            },
            complete: function() {
                checkbox.prop('disabled', false);
            }
        });
    });
}); 