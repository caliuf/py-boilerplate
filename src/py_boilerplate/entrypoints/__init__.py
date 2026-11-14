"""Superfici di ingresso (adapter driving) del progetto.

Ogni entrypoint ha la stessa anatomia: parse → validazione runtime → caso d'uso
→ mapping del risultato sul canale. Il wiring vive nel composition root.
"""
