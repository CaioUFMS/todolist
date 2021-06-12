function recuperaListas() {
    $.ajax({
        type: 'GET',
        url: '/api/listas',
        complete: function(response){
            const queryString = window.location.search;
            const urlParams = new URLSearchParams(queryString);
            const id_lista = urlParams.get('id_lista');

            let json = response.responseJSON;
            for (let i = 0; i < json.length; i++) {
                let nova_lista = document.createElement('button');
                nova_lista.id = "lista_" + json[i]['id']
                nova_lista.className= 'list-group-item list-group-item-action';
                if (i === 0) {
                    nova_lista.className= 'list-group-item list-group-item-action active';
                }
                nova_lista.innerText = json[i]['nome'];
                nova_lista.style.border = 'none';
                document.getElementById("listas").append(nova_lista);
                if (i === 0 && id_lista == null) {
                    nova_lista.click();
                }
                else {
                    if (id_lista === `${json[i]['id']}`) {
                        nova_lista.click();
                    }
                }
            }
        }
    })
}
recuperaListas();


function criar_lista(msg) {
    let json = msg.responseJSON
    let listas = document.getElementById("listas");
    let nova_lista = document.createElement('button');
    nova_lista.className= 'list-group-item list-group-item-action';
    nova_lista.innerText = json["nome"];
    nova_lista.style.border = 'none';
    nova_lista.id = 'lista_' + json['id'];
    listas.append(nova_lista);
    nova_lista.click();
}

$('#criar_lista').on('click', function(){
    $.ajax({
        type: 'POST',
        url: '/api/listas',
        complete: function(msg){
            criar_lista(msg);
        }
    })
});

function excluirLista(id_lista) {
    document.getElementsByClassName('modal-title')[0].innerText = 'Excluir lista';
    document.getElementsByClassName('modal-body')[0].innerText = 'Tem certeza que deseja excluir essa lista?';
    $('.modal').modal('show');

    $('.modal .modal-footer').off()
        .on('click', '#confirmar', function() {
            $.ajax({
                type: 'DELETE',
                url: '/api/listas/' + id_lista,
                complete: function(){
                    let lista = document.getElementById('lista_' + id_lista);
                    lista.remove();
                    let ul = document.getElementById("listas");
                    let li = ul.getElementsByClassName("list-group-item");
                    if (li.length > 0) {
                        li[0].click();
                    }
                    else {
                        document.getElementById('nome_lista').innerText = 'Selecione ou crie uma lista!';
                        document.getElementById('descricao_lista').innerText = '';
                        document.getElementById('botoes_lista').classList.add('invisible');
                        document.getElementsByClassName('progress')[0].classList.add('invisible');
                    }
                }
            })
        });
}

function criarTarefa(id_lista) {
    $.ajax({
        type: 'POST',
        url: '/api/listas/' + id_lista + '/tarefas',
        complete: function(msg){
            desenharTarefa(msg.responseJSON)
            let progressbar = document.getElementById("progresso");
            let qtd_tarefas = parseInt(localStorage.getItem('qtd_tarefas'), 10) + 1;
            let qtd_concluidas = parseInt(localStorage.getItem('qtd_concluidas'), 10);

            localStorage.setItem('qtd_tarefas', `${qtd_tarefas}`);
            let porcentagem = qtd_concluidas * 100 / qtd_tarefas;
            progressbar.style.width = porcentagem.toString() + '%';
        }
    })
}

function desenharTarefa(tarefa) {
    let tarefas = document.getElementById('tarefas');
    let url_editar_tarefa = `/listas/${tarefa['lista']}/tarefas/${tarefa['id']}/editar`;
    let concluida = '';
    if (tarefa['concluida'] === true) {
        concluida = 'checked';
    }
    let html_tarefa = `
                <div id="${tarefa['lista']}_tarefa_${tarefa['id']}" class="col">
                    <div class="card border-dark mb-3" style="max-width: 18rem;">
                        <div class="card-header justify-content-between d-flex" style="background-color: ${tarefa['cor']};">
                            <div class="text-left">
                                ${tarefa["titulo"]}
                            </div>
                            <div class="row text-right">
                                <div class="task-buttons">
                                    <a class="editar-tarefa" href="${url_editar_tarefa}">
                                        <img src="static/img/editIcon.png" width="20em" height="20em" alt="Editar Tarefa">
                                    </a>
                                    <a class="excluir-tarefa" style="cursor: pointer">
                                        <img src="static/img/deleteIcon.png" width="20em" height="20em" alt="Excluir tarefa">
                                    </a>
                                </div>
                            </div>
                        </div>
                        <div class="card-body">
                            <p class="card-text text-justify-CUSTOM">
                                ${tarefa['descricao']}
                            </p>
                        </div>
                        <div class="card-footer bg-transparent justify-content-between d-flex">
                            <div class="form-check">
                                <label class="form-check-label" for="concluido_tarefa${tarefa['id']}">
                                    Feito!
                                </label>
                                <input class="form-check-input" type="checkbox" name="exampleRadios"
                                       id="concluido_tarefa${tarefa['id']}" value="option1" ${concluida}>                            
                            </div>
                            <p class="mb-0">${tarefa['data']}</p>
                        </div>
                    </div>
                </div>
            `
    tarefas.innerHTML += html_tarefa;
}

$('#listas').on('click', 'button', function() {
    $(this).addClass('active').siblings().removeClass('active');
    let id_lista = $(this).attr('id').split('_')[1];
    $.ajax({
        type: 'GET',
        url: '/api/listas/' + id_lista,
        complete: function(msg){
            document.getElementById('nome_lista').innerText = msg.responseJSON['nome'];
            document.getElementById('descricao_lista').innerText = msg.responseJSON['descricao'];
            document.getElementById('botoes_lista').classList.remove('invisible');
            document.getElementById('editar_lista').setAttribute('href', `/listas/${id_lista}/editar`)
            document.getElementsByClassName('progress')[0].classList.remove('invisible');
            $('#botoes_lista').off()
                .on('click', '#excluir_lista', function() {excluirLista(id_lista)})
                .on('click', '#criar_tarefa', function() {criarTarefa(id_lista)});
            $('#tarefas').empty();
            let lista = msg.responseJSON;
            let tarefas = lista['tarefas'];
            let qtd_concluidas = 0;
            let qtd_tarefas = 0;
            if (tarefas) {
                tarefas.sort(function(a, b) {
                    let data1 = `${a['data']}`.split('/');
                    data1 = parseInt(`${data1[2]}${data1[1]}${data1[0]}`);
                    let data2 = `${b['data']}`.split('/');
                    data2 = parseInt(`${data2[2]}${data2[1]}${data2[0]}`);
                    return a['concluida'] - b['concluida'] || data1 - data2;
                })
                for (let i = 0; i < tarefas.length; i++) {
                    desenharTarefa(tarefas[i]);
                    if (tarefas[i]['concluida'] === true) {
                        qtd_concluidas++;
                    }
                    qtd_tarefas++;
                }
            }
            let porcentagem = '0%'
            if (qtd_tarefas !== 0) {
                porcentagem = `${qtd_concluidas*100 / qtd_tarefas}%`
            }
            document.getElementById('progresso').style.width = porcentagem;
            localStorage.setItem('qtd_tarefas', `${qtd_tarefas}`);
            localStorage.setItem('qtd_concluidas', `${qtd_concluidas}`);
        }
    })
})

$('#tarefas')
    .on('click', 'input', function(){
        let ids = $(this).parent().parent().parent().parent().attr('id').split('_');
        let id_lista = ids[0];
        let id_tarefa = ids[2];
        let checkedValue = $(this).is(':checked');
        $.ajax({
            type: 'PATCH',
            url: `api/listas/${id_lista}/tarefas/${id_tarefa}`,
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify(
                {
                    'concluida': checkedValue
                }
            ),
            complete: function(){

                let progressbar = document.getElementById("progresso");

                let qtd_concluidas = parseInt(localStorage.getItem('qtd_concluidas'), 10)
                if (checkedValue === true) {
                    qtd_concluidas++;
                    localStorage.setItem('qtd_concluidas', `${qtd_concluidas}`);
                    document.getElementById('concluido_tarefa' + id_tarefa).setAttribute('checked', 'checked');
                } else {
                    qtd_concluidas--;
                    localStorage.setItem('qtd_concluidas', `${qtd_concluidas}`);
                    document.getElementById('concluido_tarefa' + id_tarefa).removeAttribute('checked');
                }
                let qtd_tarefas = parseInt(localStorage.getItem('qtd_tarefas'), 10)
                progressbar.style.width = (qtd_concluidas * 100 / qtd_tarefas).toString() + '%';
            }
        })
    })
    .on('click', '.excluir-tarefa', function () {
        let ids = $(this).parent().parent().parent().parent().parent().attr('id').split('_');
        let id_lista = ids[0];
        let id_tarefa = ids[2];
        document.getElementsByClassName('modal-title')[0].innerText = 'Excluir tarefa';
        document.getElementsByClassName('modal-body')[0].innerText = 'Tem certeza que deseja excluir essa tarefa?';
        $('.modal').modal('show');

        $('.modal .modal-footer').off()
            .on('click', '#confirmar', function () {
                $.ajax({
                    type: 'DELETE',
                    url: `api/listas/${id_lista}/tarefas/${id_tarefa}`,
                    complete: function () {
                        let progressbar = document.getElementById("progresso");
                        let qtd_tarefas = parseInt(localStorage.getItem('qtd_tarefas'), 10) - 1;
                        localStorage.setItem('qtd_tarefas', `${qtd_tarefas}`);
                        let checkedValue = document.getElementById('concluido_tarefa' + id_tarefa).checked;

                        let qtd_concluidas = parseInt(localStorage.getItem('qtd_concluidas'), 10);
                        if (checkedValue === true) {
                            qtd_concluidas--;
                            localStorage.setItem('qtd_concluidas', `${qtd_concluidas}`);
                        }

                        let porcentagem = 0;
                        if (qtd_tarefas !== 0) {
                            porcentagem = qtd_concluidas * 100 / qtd_tarefas
                        }

                        progressbar.style.width = porcentagem.toString() + '%';
                        id_tarefa = `${id_lista}_tarefa_${id_tarefa}`
                        let tarefa = document.getElementById(id_tarefa);
                        tarefa.remove();
                    }
                })
            });
    })

function filterList() {
    let input = document.getElementById('busca');
    let filter = input.value.toUpperCase();
    if (filter.startsWith(':')) {
        filter = filter.substring(1, filter.length)
        let tarefas, tarefa, titulo;
        tarefas = document.getElementById("tarefas").getElementsByClassName("col");
        for (let i = 0; i < tarefas.length; i++) {
            tarefa = tarefas[i];
            titulo = tarefa.getElementsByClassName("text-left")[0].textContent;

            let filters = filter.split(" ");
            filters = filters.filter(f => f.length)

            let shouldDisplay = true
            filters.forEach(filt => {
                shouldDisplay = shouldDisplay && titulo.toUpperCase().includes(filt)
            })

            tarefas[i].style.display = (shouldDisplay || filters.length === 0) ? "" : "none";
        }
    }
    else {
        let ul, li, a, i, txtValue;
        ul = document.getElementById("listas");
        li = ul.getElementsByClassName("list-group-item");

        for (i = 0; i < li.length; i++) {
            a = li[i];
            txtValue = a.textContent || a.innerText;

            let filters = filter.split(" ")
            filters = filters.filter(f => f.length)

            let shouldDisplay = true

            filters.forEach(filt => {
                shouldDisplay = shouldDisplay && txtValue.toUpperCase().includes(filt)
            })

            li[i].style.display = (shouldDisplay || filters.length === 0) ? "" : "none";
        }
    }
}