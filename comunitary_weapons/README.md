# Armas Comunitarias
Modulo para las comunitarias

Objetivos del módulo

    Registrar armas disponibles para préstamo (espadas, hachas, escudos, etc.).

    Gestionar los préstamos activos: quién tomó qué arma, en qué fecha, y cuándo fue devuelta.

    Historial completo de uso, para trazabilidad y gestión del desgaste.

    Limitar acceso a préstamos: solo usuarios autorizados (organizadores) pueden prestar armas.

👥 Actores y permisos
Actor | Rol / Permiso | Funciones -- | -- | -- Organizador | Acceso total | Gestiona armas y préstamos, crea y cierra préstamos Participante | Sin acceso a backend | Solo aparece como prestatario de un arma Administrador | Gestión completa del módulo | Mismo que organizador + configuración técnica y eliminación
🧱 Modelo de datos
1. Arma (soft.weapon)

    name: Nombre del arma

    weapon_type: Tipo (espada, escudo, lanza...)

    serial: Número de serie o identificación única

    status: Disponible / Prestada / Retirada

    notes: Comentarios o historial de reparación

2. Préstamo (soft.loan)

    weapon_id: Arma prestada (Many2one → soft.weapon)

    partner_id: Persona a la que se presta (Many2one → res.partner)

    loan_date: Fecha de entrega

    return_date: Fecha de devolución (opcional si aún no fue devuelta)

    state: Borrador / Prestado / Devuelto

🖥️ UX y flujo de trabajo

    Menú principal: “Softcombat”

    Submenús:

        “Armas disponibles” (vista de lista y formulario)

        “Préstamos” (historial + activos)

    Formulario de préstamo:

        Se elige arma y persona

        Fecha de entrega automática (hoy)

        Al marcar como devuelto, se registra la fecha y cambia el estado del arma a “Disponible”

    Acciones rápidas:

        Botón “Registrar devolución”

        Filtro “Prestamos activos” (sin return_date)

🔐 Seguridad y reglas de acceso

    Grupos:

        softcombat_manager: organiza, crea y cierra préstamos

        softcombat_admin: mismo más eliminar registros

    Acceso:

        Participantes no tienen acceso al backend

    Reglas:

        No se puede prestar una arma ya prestada

        Al devolver un arma, su estado vuelve a “Disponible”
