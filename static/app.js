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

                console.log(data);

                if (data.status !== 'finished' || data.status !== 'failed') {
                    setTimeout(checkJob, 3000, jobId);
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
