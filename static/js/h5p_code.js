
function initH5P(quiz_id) {
    const el = document.querySelector("."+quiz_id);
    new H5PStandalone.H5P(el, {
        h5pJsonPath: 'h5p/'+quiz_id,
        frameJs: 'assets/h5p-standalone/dist/frame.bundle.js',
        frameCss: 'assets/h5p-standalone/dist/styles/h5p.css',
    });
    }