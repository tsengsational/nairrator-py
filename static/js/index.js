form = document.getElementById('nairrator-form')
player = document.getElementById('player')
audiotrack = document.querySelector('.audio-track img')
loader = document.querySelector('.loader')

form.addEventListener('submit', async (e) => {
    e.preventDefault()

    docId = e.target[0].value
    language = e.target[2].selectedOptions[0].value
    voice = e.target[1].selectedOptions[0].value
    console.log(docId, language, voice)
    audiotrack.classList.add('is-hidden')
    loader.classList.remove('is-hidden')
    
    fetch(`get-audio?doc_id=${docId}&lang=${language}&voice=${voice}`)
        .then(response => response.json())
        .then(data => {
            if (player.classList.contains('is-hidden')) {
                loader.classList.add('is-hidden')
                player.classList.remove('is-hidden')
                player.src = `audio/${data.doc_id}-${data.language}.mp3?dir=clips`
            }
            console.log(data)
        })
})
