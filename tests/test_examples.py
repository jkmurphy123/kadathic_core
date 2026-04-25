from examples import game_context_demo, plain_chatbot, quiz_context_demo


def test_plain_chatbot_example_runs(capsys) -> None:
    plain_chatbot.main(["--provider", "mock"])

    captured = capsys.readouterr()
    assert "[mock:mock]" in captured.out


def test_quiz_context_example_runs(capsys) -> None:
    quiz_context_demo.main(["--provider", "mock"])

    captured = capsys.readouterr()
    assert "[mock:mock]" in captured.out


def test_game_context_example_runs(capsys) -> None:
    game_context_demo.main(["--provider", "mock"])

    captured = capsys.readouterr()
    assert "[mock:mock]" in captured.out
