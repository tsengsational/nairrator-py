form = document.getElementById('nairrator-form')
player = document.getElementById('player')
audiotrack = document.querySelector('.audio-track img')

form.addEventListener('submit', async (e) => {
    e.preventDefault()

    docId = e.target[0].value
    language = e.target[2].selectedOptions[0].value
    voice = e.target[1].selectedOptions[0].value
    console.log(docId, language, voice)

    await fetch(`get-audio?doc_id=${docId}&lang=${language}&voice=${voice}`)
        .then(response => response.json())
        .then(data => {
            if (player.classList.contains('is-hidden')) {
                player.classList.remove('is-hidden')
                audiotrack.classList.add('is-hidden')
                player.src = `audio/${data.doc_id}-${data.language}.mp3?dir=clips`
            }
            console.log(data)
        })
})

player.src = `audio/7109475-english.mp3?dir=clips`