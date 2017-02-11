$(document).ready(function() {
    var jobId = '',
        jobStatus = '';

    function checkJob(jobId) {
        $.ajax({
            url: '/checkstatus/' + jobId,
            type: 'GET',
            success: function(data) {
                jobStatus = data.status;
                $('#status').text(jobStatus);

                if (data.status !== 'finished' && data.status !== 'failed') {
                    setTimeout(checkJob, 3000, jobId);
                } else {
                    for (var i = 0; i < data.result.length; i++) {
                        var name = data.result[i].name,
                            email = data.result[i].email,
                            count = data.result[i].count;

                        if (name.length <= 15 || email.length <= 15) {
                            $('#resultContent').append('<tr><td>'+ name +'</td><td>'+ email +'</td><td>'+ count +'</td></tr>');
                        }
                    }
                }
            },
            dataType: 'json'
        });
    }

    $.ajax({
        url: '/fetchmails',
        type: 'GET',
        success: function(data) {
            console.log(data);
            checkJob(data.jobId);
        },
        dataType: 'json'
    });
});
