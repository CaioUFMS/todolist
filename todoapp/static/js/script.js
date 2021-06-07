var ul = document.getElementById("color-picker");

ul.addEventListener('click', function(e) {
    let colorPickerButton = document.getElementById('color-picker-button')
    colorPickerButton.style.backgroundColor = e.target.style.backgroundColor;
    let input = document.getElementById('input-cor-tarefa')
    input.value = e.target.style.backgroundColor;
})