# R0-6E-C · Caja y gastos · guion (pasos 3–4)
🎓 Fábrica C · 21 nov 2026, 09:50 · v1 · 1 vídeo de Vera, ≈ 75 s (≈ 185 palabras) con capturas de Dinero › Caja y Dinero › Gastos
(Aquí porque el proyecto Volvera.IO está lleno; ficha, investigación y diseño en `claude/academia/cursos/R0-6E-C/`.)

## Lo que dice Vera
[Captura: Dinero › Caja, «Caja sin abrir hoy»]
Hola, soy Vera. La caja se lleva en tres momentos, y cada día.
[Captura: «Abrir caja», «Fondo de caja»]
Por la mañana, antes del primer cobro en efectivo, abres la caja con el fondo que has contado.
[Captura: «Movimiento de caja», Retirada, Pequeño gasto, Motivo]
Durante el día, cada vez que sale o entra dinero que no es un cobro, lo apuntas al momento, con un motivo que entienda otra persona: el ticket del café, el ingreso en el banco, el cambio.
[Rótulo: ⛔ 1.000 € o más · nunca en efectivo]
Y una regla que no se salta: un pago de mil euros o más no se cobra en efectivo, tampoco en dos partes. La ley suma los pagos. Tarjeta o transferencia.
[Captura: «Cerrar caja», «Efectivo contado», «Diferencia»]
Por la tarde, cuentas billetes y monedas sin mirar lo esperado y escribes lo que hay. Si no cuadra, explicas por qué, en una frase concreta. Nunca pones ni quitas dinero para que cuadre.
[Captura: Dinero › Gastos, «Puntual» y «Recurrente»]
Las facturas de lo que gasta la clínica, el mismo día que llegan, en Gastos. Qué IVA lleva cada una lo decide tu gestoría.
[Captura: «Racha: N días seguidos con caja cerrada»]
Cada lunes, mira tus días sin cierre. La meta es cero.

## Corrector (paso 4)
- ⛔ 1 reescrita: «la caja siempre cuadrará» → quitada (promesa); ahora «si no cuadra, explicas por qué».
- ⛔ 0 pendientes. Sin «IA», sin cifras de estudios, sin precios ni marcas, sin pacientes; «escuela», no «universidad».
- ⚠️ 1: el límite de 1.000 € es norma (Ley 7/2012, art. 7, BOE consolidado); releer el texto en boe.es antes de grabar; la excepción de 10.000 € (no residentes) no va en la voz, sí en la chuleta → C52.
- ⚠️ 2: «Neto devengado» y «Corregir recuento» salen en pantalla (no en la voz) → C51.
- Prueba de profundidad: ✅ cada paso tiene tarea con datos propios (fondo de hoy, movimiento de hoy, cierre de hoy, 3 gastos del mes, quién cierra, número del lunes).

## v1.1 · repaso con el código `main` 6a2a328 (Fábrica C, 21 nov 15:00)
- Todos los nombres siguen: «Caja sin abrir hoy», «Abrir caja», «Fondo de caja», «Movimiento de caja», «Retirada», «Pequeño gasto», «Cerrar caja», «Efectivo contado», «Diferencia», «Corregir recuento», «Puntual», «Recurrente», «Neto devengado», «Racha: N días seguidos con caja cerrada». **La voz no cambia.**
- ⚠️ **Quién llega:** Dinero › Caja y Dinero › Gastos solo se abren para quien administra y Finanzas (`useFinanceAccess`). Con el rol Recepción, la caja está en **Hoy › «Más» › «Caja · Ver estado»** (abrir, movimiento y cerrar), sin la racha. Gastos, no.
- **Nota nueva del paso 1 (texto, no voz):** «Si no ves Dinero en el menú, abre la caja desde Hoy, «Más», «Caja · Ver estado». Los gastos los apunta quien administra o tiene Finanzas.» Va con **C69** (`claude/academia/para-aprobar-5.md`). ⏳ Ver en Lumina con un usuario Recepción (paso 6).
