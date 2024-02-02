form = document.getElementById('nairrator-form')
form.addEventListener('submit', (e) => {
    e.preventDefault()

    docId = e.target[0].value
    language = e.target[2].selectedOptions[0].value
    voice = e.target[1].selectedOptions[0].value
    console.log(docId, language, voice)

    fetch(`/get-audio?docId=${docId}&language=${language}&voice=${voice}`)
    .then(response => response.json())
    .then(data => console.log(data))
})