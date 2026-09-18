import json


def test_index_route_returns_html(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.mimetype == 'text/html'
    assert b'Sudoku Game' in response.data


def test_new_game_route_returns_board_and_solution(client):
    response = client.get('/new?clues=35')

    assert response.status_code == 200
    assert response.is_json

    payload = response.get_json()
    assert 'puzzle' in payload
    assert 'solution' in payload
    assert len(payload['puzzle']) == 9
    assert len(payload['solution']) == 9
    assert all(len(row) == 9 for row in payload['puzzle'])
    assert all(len(row) == 9 for row in payload['solution'])


def test_check_solution_route_returns_incorrect_cells_for_wrong_board(client):
    client.get('/new?clues=35')
    wrong_board = [[0 for _ in range(9)] for _ in range(9)]

    response = client.post(
        '/check',
        data=json.dumps({'board': wrong_board}),
        content_type='application/json',
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert 'incorrect' in payload
    assert isinstance(payload['incorrect'], list)


def test_check_solution_route_handles_missing_game_state(client):
    response = client.post(
        '/check',
        data=json.dumps({'board': [[0 for _ in range(9)] for _ in range(9)]}),
        content_type='application/json',
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload['error'] == 'No game in progress'
