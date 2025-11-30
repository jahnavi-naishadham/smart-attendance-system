$(function() {
            $("#sortable-topics").sortable({
                update: function(event, ui) {
                    var order = $(this).sortable('toArray', { attribute: 'data-topic-id' });
                    $.ajax({
                        url: '{% url "reorder_topics" %}',
                        method: 'POST',
                        data: {
                            order: order,
                            csrfmiddlewaretoken: '{{ csrf_token }}'
                        },
                        success: function(response) {
                            console.log('Order updated successfully.');
                        },
                        error: function(error) {
                            console.log('Error updating order:', error);
                        }
                    });
                }
            });
            $("#sortable-topics").disableSelection();
        });

        function toggleInfoText() {
            var infoText = document.querySelector('.info-text');
            if (infoText.style.display === 'none') {
                infoText.style.display = 'block';
            } else {
                infoText.style.display = 'none';
            }
        }

        // Close the info text when clicking outside of it
        window.addEventListener('click', function(event) {
            var infoIcon = document.querySelector('.info-icon');
            var infoText = document.querySelector('.info-text');
            if (event.target !== infoIcon && !infoIcon.contains(event.target) && event.target !== infoText) {
                infoText.style.display = 'none';
            }
        });

        // Search functionality
        $("#search-box").on("input", function() {
            var query = $(this).val().toLowerCase();
            $(".topics-list li").each(function() {
                var title = $(this).find(".topic-title").text().toLowerCase();
                $(this).toggle(title.includes(query));
            });
        });
