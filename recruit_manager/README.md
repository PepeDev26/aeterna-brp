# Gestión de Reclutas

## Descripción
El módulo **Gestión de Reclutas** está diseñado para llevar un control eficiente del proceso de ingreso de nuevos miembros, conocidos como reclutas. Permite registrar la asistencia de los reclutas, verificar si cuentan con arma propia o encargada, y gestionar su aprobación a través de un flujo automatizado.

## Objetivos
- Controlar el proceso de ingreso de reclutas.
- Registrar la asistencia y verificar la disponibilidad de armas.
- Marcar reclutas como aprobados tras una evaluación externa.
- Permitir la extensión del periodo de prueba si la aprobación no es exitosa.
- Automatizar el cambio de rango a "Miembro Novato" al cumplir con los criterios establecidos.

## Funcionalidades
- Registro de reclutas con información relevante.
- Registro de asistencias que incrementa automáticamente el conteo de asistencia.
- Cambio de estado del recluta basado en criterios de evaluación.
- Interfaz de usuario intuitiva para la gestión de reclutas y asistencias.

## Modelos
- **recruit.process**: Modelo que gestiona el proceso de reclutamiento, incluyendo campos como `partner_id`, `start_date`, `tiene_arma`, `attendance_count`, `status`, `extension_weeks`, y `promotion_date`.
- **recruit.attendance**: Modelo que registra la asistencia de los reclutas, vinculándose al modelo de proceso de reclutamiento.

## Seguridad
El acceso al módulo está restringido a usuarios con el grupo `recruit_admin_group`, asegurando que solo los administradores puedan gestionar los reclutas y sus estados.

## Instalación
Para instalar el módulo, colóquelo en la carpeta de addons de su instancia de Odoo y actualice la lista de módulos. Luego, busque "Gestión de Reclutas" en la interfaz de Odoo y proceda a instalarlo.

## Uso
Una vez instalado, acceda al menú "Gestión de Reclutas" para gestionar reclutas activos y consultar el historial. Utilice las opciones disponibles para agregar asistencias, extender periodos de prueba y aprobar reclutas.

## Contribuciones
Las contribuciones son bienvenidas. Si desea colaborar, por favor, envíe un pull request o abra un issue para discutir cambios propuestos.