from datetime import datetime
from sqlmodel import select
import typer
import asyncio
from app.core.database import async_session
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.schemas.auth import AdminCreate


cli = typer.Typer()


# python3 -m app.manage create-admin --email "test@mail.com" --password "123" --name "Ben" --surname "Benov" --second_name "Benovich" --birthday "yyyy-mm-dd"
@cli.command(name='create-admin')
def create_admin(
    email: str = typer.Option(...),
    password: str = typer.Option(...),
    name: str = typer.Option(...),
    surname: str = typer.Option(...),
    second_name: str = typer.Option(..., "--second_name"),
    birthday: str = typer.Option(...),
):
    
    try:
        admin_data = AdminCreate(
            email=email, 
            password=password, 
            name=name, 
            surname=surname, 
            second_name=second_name, 
            birthday=datetime.strptime(birthday, "%Y-%m-%d").date()
        )
    except Exception as e:
        print(f"Ошибка валидации данных: {e}")
        raise typer.Exit(code=1)
    
    
    async def _logic():
        async with async_session() as session:

            result = await session.execute(select(User).where(User.email == email))
            if result.scalar_one_or_none():
                print(f"Ошибка: Пользователь с email {email} уже существует")
                return

            new_admin = User(
                **admin_data.model_dump(exclude={"password"}),
                password_hash=get_password_hash(admin_data.password),
                role=UserRole.superuser
            )
            
            session.add(new_admin)
            await session.commit()

            print(f"Суперпользователь {email} успешно создан!")

    asyncio.run(_logic())


@cli.command()
def health():
    print("OK")


if __name__ == "__main__":
    cli()