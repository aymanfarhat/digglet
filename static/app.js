$(document).ready(function() {
    var jobId = '',
        jobStatus = '';

    function checkJob(jobId) {
        $.ajax({
            url: '/checkjob/' + jobId,
            type: 'GET',
            success: function(data) {
                jobStatus = data.status;
                $('#status').text(jobStatus);

                if (data.status !== 'finished' && data.status !== 'failed') {
                    setTimeout(checkJob, 3000, jobId);
                } else {
                    for (var i = 0; i < data.result.length; i++) {
                        $('#resultContent').append('<tr><td>Alan Watts</td><td>allan@watts.com</td><td>35</td></tr>');
                    }
                }
            },
            dataType: 'json'
        });
    }

    $.ajax({
        url: '/dojob',
        type: 'GET',
        success: function(data) {
            console.log(data);
            checkJob(data.jobId);
        },
        dataType: 'json'
    });
});
