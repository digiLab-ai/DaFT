const submit = () => {
    if (!inputData) {
        alert("No data!");
        return;
    }

    $("#stageParameterise").css("display", "none");
    $("#stageProcessing").css("display", "block");

    fetch("/process", {
        method: "POST",
        body: JSON.stringify({
            data: inputData,
            n_sub: $("#parameteriseNSub").val(),
            n_pop: $("#parameteriseNPop").val(),
            n_gen: $("#parameteriseNGen").val(),
        }),
        headers: {
            "Content-Type": "application/json",
        },
    })
        .then((response) => {
            $("#stageProcessing").css("display", "none");
            $("#stageOutput").css("display", "block");
            return response.json();
        })
        .then((csv) => {
            showResult(readCsv(csv));
        })
        .catch((error) => console.log("ERROR: " + error));
};
