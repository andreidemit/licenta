"""
Utilitare pentru interpretarea tranzițiilor environment → agent.

Aceste funcții păstrează logica tabulară existentă, dar centralizează
clasificarea evenimentelor folosită de trainer, CLI și renderer.
"""


def cell_type_name(cell_type):
    """Returnează numele serializabil al tipului de celulă."""
    return cell_type.name if hasattr(cell_type, "name") else str(cell_type)


def is_collision(action, result, previous_pos):
    """
    O coliziune este o acțiune de mișcare care primește penalizare
    și nu schimbă poziția agentului.
    """
    return (
        action != 4
        and result["reward"] < 0
        and result["new_pos"] == previous_pos
    )


def build_step_feedback(action, result, previous_pos, terminal_reason=None):
    """Construiește payload-ul comun consumat de renderer și API-ul web."""
    return {
        "action": action,
        "reward": result["reward"],
        "energy_cost": result["energy_cost"],
        "energy_gain": result["energy_gain"],
        "energy_delta": result["energy_gain"] - result["energy_cost"],
        "previous_pos": previous_pos,
        "new_pos": result["new_pos"],
        "cell_type": cell_type_name(result.get("cell_type")),
        "terminal_reason": terminal_reason,
        "is_collision": is_collision(action, result, previous_pos),
    }
