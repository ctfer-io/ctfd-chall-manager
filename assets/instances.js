function get_all_instances() {
    var url = "/api/v1/plugins/ctfd-chall-manager/admin/instance"

    CTFd.fetch(url, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    }).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response.json();
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response.json();
        }
        return response.json();
    }).then(function (response) {
        if (window.t !== undefined) {
            clearInterval(window.t);
            window.t = undefined;
        }
        if (response.success) response = response.data;
        else CTFd._functions.events.eventAlert({
            title: "Fail",
            html: response.message,
            button: "OK"
        });
        if (response.remaining_time != undefined) {
            $('#whale-challenge-user-access').html(response.user_access);
            $('#whale-challenge-lan-domain').html(response.lan_domain);
            $('#whale-challenge-count-down').text(response.remaining_time);
            $('#whale-panel-stopped').hide();
            $('#whale-panel-started').show();

            window.t = setInterval(() => {
                const c = $('#whale-challenge-count-down').text();
                if (!c) return;
                let second = parseInt(c) - 1;
                if (second <= 0) {
                    loadInfo();
                }
                $('#whale-challenge-count-down').text(second);
            }, 1000);
        } else {
            $('#whale-panel-started').hide();
            $('#whale-panel-stopped').show();
        }
    });
};