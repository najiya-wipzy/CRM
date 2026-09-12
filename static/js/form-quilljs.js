document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll(".snow-editor").forEach((el) => {

        new Quill(el, {
            theme: "snow",
            modules: {
                toolbar: [
                    ["bold", "italic", "underline"],
                    [{ header: [1, 2, 3, 4, 5, 6, false] }],
                    [{ list: "ordered" }, { list: "bullet" }],
                    ["link", "image", "video"]
                ]
            }
        });

    });

});