# Forja Basica de Aeterna
Nombre del módulo:

Gestor de Forja

🎯 Objetivos del módulo

- Gestionar el avance de creación de armas artesanales en la forja.
- Permitir visualizar el progreso por etapas en una vista Kanban.
- Llevar control de fechas, materiales y responsables del proceso.
- Centralizar tareas de forja por arma y facilitar el seguimiento.

👥 Actores y Roles
Actor | Rol / Permisos | Funciones principales
-- | -- | --
Forjador | Acceso completo | Registra, edita y avanza armas en proceso
Administrador | Configura el módulo | Puede eliminar o modificar flujos completos

🔗 Relación con Contactos

- Cada arma puede tener asignado un contacto (forjador o destinatario final).
- Opcional: vincular también a reclutas que encargan armas desde el módulo de reclutamiento.

📊 Etapas del Proceso (Vista Kanban)

- Diseño
- Preparación de materiales
- Montaje inicial
- Revestimiento / acabado
- Listo para entrega
- Entregado

Cada arma puede moverse de una etapa a otra desde el Kanban con drag & drop.

🧰 Modelo de Datos
1. forge.weapon
    - name: Nombre del arma
    - weapon_type: Tipo de arma (espada, escudo, lanza, etc.)
    - responsible_id: Usuario o contacto a cargo de su creación (Many2one)
    - stage_id: Etapa actual (Many2one hacia forge.stage)
    - requested_by_id: Contacto que solicitó el arma (opcional)
    - start_date: Fecha de inicio de la forja
    - end_date: Fecha estimada de finalización
    - materials_notes: Texto libre con materiales utilizados

2. forge.stage
    - name: Nombre de la etapa (Diseño, Montaje, etc.)
    - sequence: Orden de aparición
    - fold: Booleano (para ocultar columnas en Kanban si están vacías)

📅 Flujo de Trabajo y UX

- Menú: "Forja de Armas"
    - Submenús: "Armas en proceso", "Historial", "Etapas"
- Vista por defecto: Kanban
- Formulario de arma:
    - Selector de etapa actual
    - Campos de responsable y solicitante
    - Fecha inicio y fin estimada
- Botones rápidos:
    - Marcar como entregada
    - Imprimir ficha de forja (QWeb opcional)

🔐 Seguridad

- Grupo forge_user: puede crear y actualizar armas, pero no eliminarlas.
- Grupo forge_admin: control total.
- Regla: solo ver las armas asignadas o creadas por el usuario (opcional).