async function import_challenge(challengeId) {
    let params = {
        "challengeId": challengeId.toString(),
    };
    let pg = CTFd.ui.ezq.ezProgressBar({
        width: 10,
        title: "Import in progress",
    });
    let response = await CTFd.fetch("/api/v1/plugins/ctfd-chall-manager/admin/import", {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify(params)
    });
    response = await response.json();
    pg = CTFd.ui.ezq.ezProgressBar({
        target: pg,
        width: 100,
    })

    return response;
}

$(".import-challenge").click(function (e) {
    e.preventDefault();
    let challengeId = $(this).attr("challenge-id");

    CTFd.ui.ezq.ezQuery({
        title: "Import",
        body: "<span>Are you sure you want to import this challenge on chall-manager?</span>",
        success: async function () {
            await import_challenge(challengeId);
            location.reload();
        }
    });
});

