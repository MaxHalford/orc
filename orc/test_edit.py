import pytest
import orc


@pytest.mark.parametrize(
    "source,target,edits",
    (
        cases := [
            # This example comes from the regex library documentation
            (
                "anacondfuuoo bar",
                "anaconda foo bar",
                orc.Edits(
                    insertions=[orc.Insertion(7, "a"), orc.Insertion(8, " ")],
                    deletions=[orc.Deletion(10), orc.Deletion(11)],
                ),
            ),
            (
                "2021-02-04",
                "2020-2-05",
                orc.Edits(
                    substitutions=[
                        orc.Substitution(at=3, new="0"),
                        orc.Substitution(at=9, new="5"),
                    ],
                    deletions=[orc.Deletion(at=5)],
                ),
            ),
        ]
    ),
    ids=[f"{source} -> {target}" for source, target, _ in cases],
)
def test_do(source: str, target: str, edits: orc.Edits):
    assert edits.do(source) == target
