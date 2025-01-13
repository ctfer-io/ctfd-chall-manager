async function delete_instance(challengeId, sourceId) {
    let params = {
        "challengeId": challengeId.toString(),
        "sourceId": sourceId.toString()
    };
    let response = await CTFd.fetch("/api/v1/plugins/ctfd-chall-manager/admin/instance" , {
        method: "DELETE",
        credentials: "same-origin",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify(params)
    });
    console.log(response)
    response = await response.json();
    return response;
}

async function renew_instance(challengeId, sourceId) {
    let params = {
        "challengeId": challengeId.toString(),
        "sourceId": sourceId.toString()
    };
    let response = await CTFd.fetch("/api/v1/plugins/ctfd-chall-manager/admin/instance", {
        method: "PATCH",
        credentials: "same-origin",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify(params)
    });
    console.log(response)
    response = await response.json();
    return response;
}

async function create_instance(challengeId, sourceId) {
    var params = {
        "challengeId": challengeId.toString(),
        "sourceId": sourceId.toString()
    };
    let response = await CTFd.fetch("/api/v1/plugins/ctfd-chall-manager/admin/instance", {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify(params)
    });
    console.log(response)
    response = await response.json();
    return response;
}

function parseRange(input) {
    var sourceIds = []
    const pattern = /\d+-\d+/
    elem = input.split(',')
    
    for (let i=0; i<elem.length;i++){
        if (pattern.test(elem[i])){
            let low = Number(elem[i].split('-')[0])
            let high = Number(elem[i].split('-')[1])
            for (let j=low; j<=high;j++){
                sourceIds.push(Number(j))
            }
        } else {
            sourceIds.push(Number(elem[i]))
        }
    }
    return sourceIds.sort((a, b) => a - b);
}

$(".delete-instance").click(function (e) {
    e.preventDefault();
    let challengeId = $(this).attr("challenge-id");
    let sourceId = $(this).attr("source-id");

    CTFd.ui.ezq.ezQuery({
        title: "Destroy",
        body: "<span>Are you sure you want to delete this instance?</span>",
        success: async function () {
            await delete_instance(challengeId, sourceId);
            location.reload();
        }
    });
});

$(".restart-instance").click(function (e) {
    e.preventDefault();
    let challengeId = $(this).attr("challenge-id");
    let sourceId = $(this).attr("source-id");

    CTFd.ui.ezq.ezQuery({
        title: "Restart",
        body: "<span>Are you sure you want to restart this instance?</span>",
        success: async function () {
            await delete_instance(challengeId, sourceId);
            await create_instance(challengeId, sourceId);
            location.reload();
        }
    });
});

$(".renew-instance").click(function (e) {
    e.preventDefault();
    let challengeId = $(this).attr("challenge-id");
    let sourceId = $(this).attr("source-id");

    CTFd.ui.ezq.ezQuery({
        title: "Renew",
        body: "<span>Are you sure you want to renew this instance?</span>",
        success: async function () {
            await renew_instance(challengeId, sourceId);
            location.reload();
        }
    });
});


$('#instances-restart-button').click(function (e) {
    // This is bulk function

    let sourceId = $("input[data-source-id]:checked").map(function () {
        return $(this).data("source-id");
    });

    let challengeId = $("input[data-challenge-id]:checked").map(function () {
        return $(this).data("challenge-id");
    });

    let challengeIds = challengeId.toArray();
    let sourceIds = sourceId.toArray();

    CTFd.ui.ezq.ezQuery({
        title: "Restart Instances",
        body: `Are you sure you want to delete and create the selected ${sourceIds.length} instance(s)?`,
        success: async function () {
            var pg = CTFd.ui.ezq.ezProgressBar({
                width: 0,
                title: "Restart in progress",
            });

            let totalInstances = sourceIds.length * 2;
            let deletedInstances = 0;
            let createdInstances = 0;

            let instancePromises = [];

            for (let i = 0; i < sourceIds.length; i++) {
                instancePromises.push(
                    delete_instance(challengeIds[i], sourceIds[i])
                        .then(() => {
                            deletedInstances++;
                            var width = ((deletedInstances + createdInstances)/ totalInstances) * 100;
                            pg = CTFd.ui.ezq.ezProgressBar({
                                target: pg,
                                width: width,
                            });
                        })
                );
            }
            // trigger all delete
            await Promise.all(instancePromises)

            // reset Promises for POST
            instancePromises = []

            for (let i = 0; i < sourceIds.length; i++) {
                instancePromises.push(
                    create_instance(challengeIds[i], sourceIds[i])
                        .then(() => {
                            createdInstances++;
                            var width = ((deletedInstances + createdInstances)/ totalInstances) * 100;
                            pg = CTFd.ui.ezq.ezProgressBar({
                                target: pg,
                                width: width,
                            });
                    })
                );
            }

            await Promise.all(instancePromises)

            setTimeout(function () {
                pg.modal("hide");
            }, 500);
            location.reload();
        }
    });
});

$('#instances-delete-button').click(function (e) {
    // This is bulk function

    let sourceId = $("input[data-source-id]:checked").map(function () {
        return $(this).data("source-id");
    });

    let challengeId = $("input[data-challenge-id]:checked").map(function () {
        return $(this).data("challenge-id");
    });

    let challengeIds = challengeId.toArray();
    let sourceIds = sourceId.toArray();

    CTFd.ui.ezq.ezQuery({
        title: "Delete Instances",
        body: `Are you sure you want to delete the selected ${sourceIds.length} instance(s)?`,
        success: async function () {
            var pg = CTFd.ui.ezq.ezProgressBar({
                width: 0,
                title: "Deleting progress",
            });

            let totalInstances = sourceIds.length;
            let deletedInstances = 0;

            let instancePromises = [];

            for (let i = 0; i < sourceIds.length; i++) {
                instancePromises.push(
                    delete_instance(challengeIds[i], sourceIds[i]).then(() => {
                        deletedInstances++;
                        var width = (deletedInstances / totalInstances) * 100;
                        pg = CTFd.ui.ezq.ezProgressBar({
                            target: pg,
                            width: width,
                        });
                    })
                );
            }

            await Promise.all(instancePromises);

            setTimeout(function () {
                pg.modal("hide");
            }, 500);
            location.reload();
        }
    });
});


$('#instances-renew-button').click(function (e) {
    let sourceId = $("input[data-source-id]:checked").map(function () {
        return $(this).data("source-id");
    });

    let challengeId = $("input[data-challenge-id]:checked").map(function () {
        return $(this).data("challenge-id");
    });

    let challengeIds = challengeId.toArray();
    let sourceIds = sourceId.toArray();

    CTFd.ui.ezq.ezQuery({
        title: "Renew Containers",
        body: `Are you sure you want to renew the selected ${sourceIds.length} instance(s)?`,
        success: async function () {
            var pg = CTFd.ui.ezq.ezProgressBar({
                width: 0,
                title: "Renewal progress",
            });

            let totalInstances = sourceIds.length;
            let renewedInstances = 0;

            let instancePromises = [];

            for (let i = 0; i < sourceIds.length; i++) {
                instancePromises.push(
                    renew_instance(challengeIds[i], sourceIds[i]).then(() => {
                        renewedInstances++;
                        var width = (renewedInstances / totalInstances) * 100;
                        pg = CTFd.ui.ezq.ezProgressBar({
                            target: pg,
                            width: width,
                        });
                    })
                );
            }

            await Promise.all(instancePromises);

            setTimeout(function () {
                pg.modal("hide");
            }, 500);
            location.reload();
        }
    });
});

$('#instances-create-button').click(function (e) {

    let sourceIds = parseRange(document.getElementById("panel-source-pattern").value)

    let challengeId = $("input[data-challenge-id]:checked").map(function () {
        return $(this).data("challenge-id");
    });

    let challengeIds = challengeId.toArray()

    CTFd.ui.ezq.ezQuery({
        title: "Create instances",
        body: `Are you sure you want to create the selected ${sourceIds.length * challengeIds.length} instance(s)?`,
        success: async function () {
            var pg = CTFd.ui.ezq.ezProgressBar({
                width: 0,
                title: "Creation progress",
            });

            let totalInstances = sourceIds.length * challengeIds.length;
            let createdInstances = 0;

            let instancePromises = [];

            for (let i = 0; i < sourceIds.length; i++) {
                for (let j = 0; j < challengeIds.length; j++) {
                    instancePromises.push(
                        create_instance(challengeIds[j], sourceIds[i]).then(() => {
                            createdInstances++;
                            var width = (createdInstances / totalInstances) * 100;
                            pg = CTFd.ui.ezq.ezProgressBar({
                                target: pg,
                                width: width,
                            });
                        })
                    );
                }
            }

            await Promise.all(instancePromises);

            setTimeout(function () {
                pg.modal("hide");
            }, 500);
        }
    });
});

function copyToClipboard(event, str) {
    // Select element
    const el = document.createElement('textarea');
    el.value = str;
    el.setAttribute('readonly', '');
    el.style.position = 'absolute';
    el.style.left = '-9999px';
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);

    $(event.target).tooltip({
        title: "Copied!",
        trigger: "manual"
    });
    $(event.target).tooltip("show");

    setTimeout(function () {
        $(event.target).tooltip("hide");
    }, 1500);
}

$(".click-copy").click(function (e) {
    copyToClipboard(e, $(this).data("copy"));
})


