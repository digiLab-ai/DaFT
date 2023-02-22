let inputData = null;

function readCsv(csv) {
    const rows = csv.split("\n");

    let data = [];
    for (let row of rows) {
        let cols = row.match(/(?:\"([^\"]*(?:\"\"[^\"]*)*)\")|([^\",]+)/g);
        if (cols) {
            data.push(cols);
        }
    }

    return data;
}

window.addEventListener("load", (_event) => {
    $("#fileElem").val("");

    let reader = new FileReader();
    let picker = $("#fileElem")[0];

    picker.onchange = () => {
        $("#stageInput").css("display", "none");
        reader.readAsText(picker.files[0]);
    };

    reader.onloadend = () => {
        inputData = readCsv(reader.result);
        $("#parameteriseNSub").val(Math.round(inputData.length * 0.2));
        $("#parameteriseNSub").attr("max", inputData.length - 1);
        $("#displayNSub").html($("#parameteriseNSub").val());
        $("#displayNPop").html($("#parameteriseNPop").val());
        $("#displayNGen").html($("#parameteriseNGen").val());
        $("#stageParameterise").css("display", "block");
    };
});
