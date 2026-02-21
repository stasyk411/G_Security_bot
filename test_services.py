"""
Тестирование работы сервисов GBR Security System
"""

from app.services import UnitService, CallService


def test_services():
    """Тестирование всех сервисов"""
    print("🧪 Тестирование сервисов GBR Security System")
    print("=" * 50)
    
    try:
        # Тестирование UnitService
        print("\n1. 📋 Тестирование UnitService")
        print("-" * 30)
        
        # Создание экипажей
        unit1 = UnitService.create_unit("ГБР-Тест-1", "111111111", "+79001111111", "Тестовый экипаж 1")
        unit2 = UnitService.create_unit("ГБР-Тест-2", "222222222", "+79002222222", "Тестовый экипаж 2")
        
        print(f"✅ Создан экипаж: {unit1.name} (ID: {unit1.id})")
        print(f"✅ Создан экипаж: {unit2.name} (ID: {unit2.id})")
        
        # Получение свободных экипажей
        free_units = UnitService.get_free_units()
        print(f"✅ Свободных экипажей: {len(free_units)}")
        
        # Изменение статуса
        updated_unit = UnitService.set_unit_status(unit1.id, 'busy')
        print(f"✅ Статус экипажа {unit1.name} изменен на: {updated_unit.status.value}")
        
        # Проверка свободных экипажей после изменения
        free_units_after = UnitService.get_free_units()
        print(f"✅ Свободных экипажей после изменения: {len(free_units_after)}")
        
        # Тестирование CallService
        print("\n2. 📞 Тестирование CallService")
        print("-" * 30)
        
        # Создание вызовов
        call1 = CallService.create_call(
            "Торговый центр 'Мега'", 
            "ул. Ленина, д. 100",
            "Сработка сигнализации",
            "55.7558",
            "37.6176"
        )
        
        call2 = CallService.create_call(
            "Офис 'Центр'", 
            "ул. Советская, д. 50",
            "Пожарная тревога",
            "55.7520",
            "37.6175"
        )
        
        print(f"✅ Создан вызов: {call1.object_name} (ID: {call1.id})")
        print(f"✅ Создан вызов: {call2.object_name} (ID: {call2.id})")
        
        # Получение ожидающих вызовов
        pending_calls = CallService.get_pending_calls()
        print(f"✅ Ожидающих вызовов: {len(pending_calls)}")
        
        # Назначение вызова на экипаж
        assigned_call = CallService.assign_call_to_unit(call1.id, unit2.id)
        print(f"✅ Вызов {call1.object_name} назначен на экипаж {unit2.name}")
        print(f"   Статус вызова: {assigned_call.status.value}")
        
        # Изменение статуса вызова
        in_progress_call = CallService.set_call_status(call1.id, 'in_progress')
        print(f"✅ Статус вызова изменен на: {in_progress_call.status.value}")
        
        # Завершение вызова
        completed_call = CallService.set_call_status(call1.id, 'completed')
        print(f"✅ Вызов завершен: {completed_call.status.value}")
        
        # Проверка статуса экипажа после завершения
        final_unit = UnitService.get_unit_by_id(unit2.id)
        print(f"✅ Финальный статус экипажа {unit2.name}: {final_unit.status.value}")
        
        # Получение всех вызовов
        all_calls = CallService.get_all_calls()
        print(f"✅ Всего вызовов в системе: {len(all_calls)}")
        
        print("\n🎉 Все тесты успешно пройдены!")
        print("=" * 50)
        
        # Итоговая статистика
        print("\n📊 Итоговая статистика:")
        all_units = UnitService.get_all_units()
        print(f"   - Всего экипажей: {len(all_units)}")
        print(f"   - Свободных экипажей: {len(UnitService.get_free_units())}")
        print(f"   - Всего вызовов: {len(all_calls)}")
        print(f"   - Ожидающих вызовов: {len(CallService.get_pending_calls())}")
        print(f"   - Активных вызовов: {len(CallService.get_active_calls())}")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(test_services())
